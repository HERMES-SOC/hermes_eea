import numpy as np
from hermes_core import log
from hermes_eea.io import EEA
from hermes_eea.util.time import ccsds_to_cdf_time
from hermes_eea.io.EEA import (
    MAX_STEPS,
    N_AZIMUTH,
    PULSE_A_CHANNEL,
    PULSE_B_CHANNEL,
    REAL4FILL,
    EPOCHTIMEFILL,
    INTFILL,
)


def skymap_factory(l0_cdf, stepper, myEEA):
    """This may eventually be handled in a python multiprocessor module instance:
    ['Epoch', 'Epoch_plus_var', 'Epoch_minus_var', 'hermes_eea_step_counter',
     'hermes_eea_counter1', 'hermes_eea_counter2', 'hermes_eea_accumulations',
     'hermes_ eea_sector_index', 'hermes_eea_sector_label'])

    Parameters
    -----------
    l0_cdf - output of CCSDS.py - each defined variable is parsed into packet arrays
    energies - the energy profile
    deflections - the 4 angles at each energy. Both of these are extracted from the stepper table.
    myEEA - a class where I put the data before loading it into the CDF.

    science_data:
    In the test data, several 'integrates' occurred signified by
     a SHEID of 0. The start of a science data energy sweep is when
     SHEID (secondary header ID) is 1
    """

    # l0_cdf["SHEID"] is 1 tells us this is a science packet, part of the sweep. often a file will have 
    # a bunch or 0s at the beginning.
    sheid_science_packets = np.where(l0_cdf["SHEID"][:] == 1)[0]
    if len(sheid_science_packets) == 0:
        log.error(
            "No science data (SHEID==1) packets found; nothing to process. "
            f"First {min(20, len(l0_cdf['SHEID']))} SHEIDs found (SHEIDS which have science data are == 1): "
            f"{l0_cdf['SHEID'][:20]}"
        )
        return
    log.info(f"Number of science packets found {len(sheid_science_packets)}")
    start_of_good_data = sheid_science_packets[0]
    # how much trailing not science data: Integrates are SHEID==0 packets
    integrates_at_end = np.where(l0_cdf["SHEID"][start_of_good_data:] == 0)
    if len(integrates_at_end[0]) > 0:
        log.warning(
            f"{len(integrates_at_end[0])} trailing integrate packets found at the end of the science data."
        )
        # We are expecting integrates to be only at the beginning

    # The Science Data, naturally:
    stepper_table_packets = (np.where(l0_cdf["SHEID"][:] > 0))[0]
    return_package = {}
    # the packets start when STEP is 0
    # the packets are sciencedata when SHEID is 1
    # nominally stepper_table_packets[0] will be 0 (no integrates at the beginning)

    # the starting packet of each sweep: (For our initial, testing stepper table, the STEPS climb from 0 to 163 repeatedly)
    # or rise and from energy 0 to energy 63 twice over four declination angles
    # the packet is very helpfull in that it tells us where the beginning of each sweep is. lo
    beginning_packets = (
        np.where((l0_cdf["STEP"][stepper_table_packets[0] :]) == 0)[0]
        + stepper_table_packets[0]
    )
    # the real sweep count, from actual STEP==0 boundaries -- NOT total_packets/len(stepper.energies),
    # since dropped packets make many sweeps irregular (shorter or longer than a full stepper table pass)
    log.info(f"Number of sweeps found: {len(beginning_packets)}")

    # convert CCSDS coarse+fine times to CDF epoch times for all packets
    epochs = ccsds_to_cdf_time.help_convert_eaa(l0_cdf)
    n_packets_total = len(epochs)

    long_sweeps, short_sweeps = find_irregular_sweeps(beginning_packets, stepper, n_packets_total)
    if long_sweeps:
        log.warning(
            f"{len(long_sweeps)} irregular sweep(s) are longer than len(stepper.energies)="
            f"{len(stepper.energies)} packets (sweep_index: actual_length): {long_sweeps}"
        )
    if short_sweeps:
        log.warning(
            f"{len(short_sweeps)} irregular sweep(s) are shorter than len(stepper.energies)="
            f"{len(stepper.energies)} packets (sweep_index: actual_length): {short_sweeps}"
        )

    
    # Now let's populate one sweep at a time and eventually the whole file
    package = []
    # ccsds coarse+fine -> cdf-epoch times.
    for ptr in range(len(beginning_packets)):
        start_idx = beginning_packets[ptr]
        finish_idx = beginning_packets[ptr + 1] if ptr + 1 < len(beginning_packets) else n_packets_total
        if ptr in long_sweeps:
            # already known (from find_irregular_sweeps) to overrun the stepper table --
            log.warning(
                f"Sweep {ptr} ({long_sweeps[ptr]} packets) exceeds the stepper table's "
                "length, likely due to lost/missing packets; skipping this sweep."
            )
            continue
        # recomputed per sweep so each sweep's own step count/range is used,
        # rather than reusing whatever length the first sweep happened to have
        try:
            step_values = manage_stepper_table_energies_and_angles(
                beginning_packets, stepper, ptr, n_packets_total, l0_cdf["STEP"]
            )
        except IndexError:
            # safety net for any other way a sweep's STEP values could index outside the
            # stepper table (e.g. a corrupted/out-of-range STEP field), not the long-sweep
            # case above, which is already caught deterministically
            log.warning(
                f"Sweep {ptr} ({finish_idx - start_idx} packets) raised an unexpected indexing "
                "error against the stepper table, likely due to a corrupted STEP value; skipping this sweep."
            )
            continue
        # ACCUM carries 34 raw channels per packet: the first N_AZIMUTH (32) are real
        # sky-map azimuth bins; the last two are TOF-ASIC overflow counters (see
        # hermes_eea.io.EEA PULSE_A_CHANNEL/PULSE_B_CHANNEL), not azimuth measurements,
        # so they're split out here rather than copied into the skymap as if they were.
        accum_slice = l0_cdf["ACCUM"][start_idx:finish_idx]
        # So note here we are appending the entire sweep's worth of data to the package, not just a single packet.
        # Note here the the eppending object is the do_eea_sweeps params: counts, pulse_a, pulse_b, cnt1, cnt2, epoch, energy_vals, deflection_vals, ith_FSmap
        package.append(
            (
                accum_slice[:, :N_AZIMUTH],  # the skymap: 32 real azimuth bins
                accum_slice[:, PULSE_A_CHANNEL],  # TOF channel A overflow counter
                accum_slice[:, PULSE_B_CHANNEL],  # TOF channel B overflow counter
                l0_cdf["COUNTER1"][start_idx:finish_idx],  # e.g. l0_cdf["COUNTER1"][47] = 12
                l0_cdf["COUNTER2"][start_idx:finish_idx],  # l0_cdf["COUNTER2"][47] = 12
                epochs[start_idx:finish_idx],
                step_values['energy'],  # from the stepper table
                step_values['elevation_angle'],  # from the stepper table
                ptr,
            )
        )

    result = []
    for sweep in package:
        sweep_contents = do_eea_sweep(*sweep)
        if sweep_contents is not None:
            result.append(sweep_contents)
    myEEA.populate(result)


def do_eea_sweep(counts, pulse_a, pulse_b, cnt1, cnt2, epoch, energy_vals, deflection_vals, ith_FSmap):
    """
    This function populates the return dictionary for one sweep. All of the
    per-sweep slicing/splitting (ACCUM into counts vs. pulse_a/pulse_b, and the
    stepper-table lookup into energy_vals/deflection_vals) has already been done
    by the caller, skymap_factory(); this function just gathers those already-arranged
    values and pads each of them out to a fixed MAX_STEPS length with fill values.

    Parameters
    ----------
    counts              - 32 real azimuth bins, already split from the raw ACCUM field in skymap_factory()
    pulse_a             - TOF channel A overflow counter (raw ACCUM bin 33), one value per packet,
                          already split from ACCUM in skymap_factory()
    pulse_b             - TOF channel B overflow counter (raw ACCUM bin 32), one value per packet,
                          already split from ACCUM in skymap_factory()
    cnt1                - the sum of this sweep's accum
    cnt2                - same as above but +1...not clear yet
    epoch               - CDF Formatted time for every single measurement, [0] is the time for the sweep/packet
    energy_vals         - this sweep's energy profile, already looked up from the stepper table in skymap_factory()
    deflection_vals     - this sweep's deflection-angle profile, already looked up from the stepper table in skymap_factory()
    ith_FSmap           - sweep counter

    Returns
    -------
    return_package : dict
        This sweep's values, each padded/fill-stuffed out to MAX_STEPS, keyed by
        "Epoch", "usec", "counts", "pulse_a", "pulse_b", "energies", "deflections",
        "counter1", "counter2".
    """
    return_package = {}
    
    return_package["Epoch"]  = epoch[0]     # here the "Epoch" is the traditional one: the start time of each sweep
   
    # Fills this key with all of the Epoch times in the sweep for  (depends on the stepper table length,
    # (so far 63 and 164) and fills out to 256 with fill values
    return_package["usec"]   = stuff_stepsize(epoch, (MAX_STEPS), EPOCHTIMEFILL) 
    
    # counts has already been sliced to the 32 real azimuth bins in skymap_factory();
    # here we just gather it into a fixed MAX_STEPS x N_AZIMUTH array
    return_package["counts"] = np.full((MAX_STEPS, N_AZIMUTH), REAL4FILL)
    return_package["counts"][0:counts.shape[0], 0:counts.shape[1]] = counts

    # pulse_a/pulse_b were already split out of the raw ACCUM field's last two channels
    # in skymap_factory(); here we just gather them into the dictionary, fill-stuffed to MAX_STEPS
    return_package["pulse_a"] = stuff_stepsize(pulse_a, (MAX_STEPS), INTFILL)  # TOF channel A overflow counter, one per packet
    return_package["pulse_b"] = stuff_stepsize(pulse_b, (MAX_STEPS), INTFILL)  # TOF channel B overflow counter, one per packet

    #  Since we might have several different stepper tables, we aren't putting them into separate
    #  energy/deflection dimensions. energy_vals was already looked up from the stepper table
    #  in skymap_factory(); here we just gather it into the dictionary, fill-stuffed to MAX_STEPS
    return_package["energies"]    = stuff_stepsize(energy_vals, (MAX_STEPS), REAL4FILL)  # a static thing for each stepper table

    # Note: the stepper table isn't just a list of energies and angles, it is also a description
    # of the sweep. e.g. if the sweep is just at one angle, the the deflection_vals will be that one
    # angle repeated for every energy step. If the sweep goes up and down across multiple angles,
    # the stepper table's deflection_vals will reflect that pattern for each energy step.
    # deflection_vals was already looked up from the stepper table in skymap_factory(); here we
    # just gather it into the dictionary, fill-stuffed to MAX_STEPS
    return_package["deflections"] = stuff_stepsize(deflection_vals, (MAX_STEPS), REAL4FILL)  # a static thing for each stepper table

    return_package["counter1"]    = stuff_stepsize(cnt1, (MAX_STEPS), INTFILL)         # number of counts in each packet (not each sweep)

    return_package["counter2"]    = stuff_stepsize(cnt2, (MAX_STEPS), INTFILL)         # number of counts in each packet

    return return_package


def find_irregular_sweeps(beginning_packets, stepper, n_packets_total):
    """
    Check every sweep's packet count (gap between consecutive beginning_packets
    entries) against len(stepper.energies), the number of steps a full sweep should have.

    Returns
    -------
    (long_sweeps, short_sweeps) - each a dict mapping sweep_index -> actual_length,
    for sweeps longer than, respectively shorter than, len(stepper.energies).
    """
    expected_len = len(stepper.energies)
    long_sweeps = {}
    short_sweeps = {}
    for ptr in range(len(beginning_packets)):
        if ptr + 1 < len(beginning_packets):
            actual_len = beginning_packets[ptr + 1] - beginning_packets[ptr]
        else:
            actual_len = n_packets_total - beginning_packets[ptr]
        if actual_len > expected_len:
            long_sweeps[ptr] = actual_len
        elif actual_len < expected_len:
            short_sweeps[ptr] = actual_len
    log.info(f"n short sweeps found:  {len(short_sweeps)}")
    log.info(f"n long sweeps found:   {len(long_sweeps)}") 
    log.info(f'n total sweeps found:  {len(beginning_packets)}')
    log.info (f"average length of short sweeps: {np.mean(list(short_sweeps.values())) if short_sweeps else 0}")
    log.info (f"average length of long sweeps: {np.mean(list(long_sweeps.values())) if long_sweeps else 0}")
    return long_sweeps, short_sweeps


def manage_stepper_table_energies_and_angles(beginning_packets, stepper, packet, npackets, steps):
    """
    Look up this sweep's energy/deflection-angle values from the stepper table, indexed by
    each retained packet's own STEP field (not its position within the sweep), so a dropped
    packet doesn't shift/misalign the lookup for every packet after the gap.

    Parameters
    ----------
    beginning_packets - packet indices where STEP==0, i.e. the start of each sweep
    stepper           - the StepperTable providing .energies/.deflections, indexed by STEP value
    packet            - which sweep to build values for (an index into beginning_packets)
    npackets          - total packet count in the file; used as the end boundary when
                        `packet` is the last, possibly-incomplete sweep
    steps             - l0_cdf["STEP"], this file's per-packet STEP field

    Returns
    -------
    stepvalues : dict
        {"energy": ndarray, "elevation_angle": ndarray} - one stepper-table value per
        packet actually present in this sweep (length == this sweep's real packet count,
        which may differ from a full stepper-table pass if packets were dropped).
    """

    stepvalues = {}
    stepvalues['energy'] = []
    stepvalues['elevation_angle'] = []

    if len(beginning_packets) == 0:
        log.warning("No sweep-start (STEP==0) packets found; nothing to process.")
        stepvalues['energy'] = np.array(stepvalues['energy'])
        stepvalues['elevation_angle'] = np.array(stepvalues['elevation_angle'])
        return stepvalues

    finish = npackets
    try:
        if beginning_packets[packet + 1]:
            finish = beginning_packets[packet+1]
    except (TypeError, IndexError):
        pass  # we are in last incomplete packet
    
    # index the stepper table by each packet's own STEP value, not its position
    # within the sweep, so a dropped packet (which shortens the retained sweep
    # but doesn't shift the surviving packets' STEP values) doesn't misalign
    # every subsequent packet's energy/deflection assignment
    for i in range(beginning_packets[packet], finish):
        step_in_sweep = steps[i]
        stepvalues['energy'].append(stepper.energies[step_in_sweep])
        stepvalues['elevation_angle'].append(stepper.deflections[step_in_sweep])
    stepvalues['energy'] = np.array( stepvalues['energy'] ) 
    stepvalues['elevation_angle'] = np.array( stepvalues['elevation_angle'] ) 
    return stepvalues


def stuff_stepsize(vals, maxsteps: tuple, fill):
    """
    SPDF won't allow variable size variables
    """
    default_size                   = np.full(maxsteps, fill)  
    default_size[0:vals.shape[0]]  = vals  
    return default_size

    