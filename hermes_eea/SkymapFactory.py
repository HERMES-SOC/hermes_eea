import numpy as np
from hermes_core import log
from hermes_eea.io import EEA
from hermes_eea.util.time import ccsds_to_cdf_time
from hermes_eea.io.EEA import MAX_STEPS, N_AZIMUTH, REAL4FILL, EPOCHTIMEFILL, INTFILL


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

    # SHEID is 1
    start_of_good_data = np.where(l0_cdf["SHEID"][:] == 1)[0][0]
    # how much trailing not science data:
    integrates_at_end = np.where(l0_cdf["SHEID"][start_of_good_data:] == 0)
    # We are expecting integrates to be only at the beginning

    # The Science Data:
    stepper_table_packets = (np.where(l0_cdf["SHEID"][:] > 0))[0]
    return_package = {}
    # the packets start when STEP is 0
    # the packets are sciencedata when SHEID is 1
    # nominally stepper_table_packets[0] will be 0 (no integrates at the beginning)

    # the starting packet of each sweep: (For our initial, testing stepper table, the STEPS climb from 0 to 163 repeatedly)
    beginning_packets = (
        np.where((l0_cdf["STEP"][stepper_table_packets[0] :]) == 0)[0]
        + stepper_table_packets[0]
    )

    epochs = ccsds_to_cdf_time.help_convert_eaa(l0_cdf)
    step_values = manage_stepper_table_energies_and_angles(beginning_packets, stepper, 0, len(epochs))
    # This is done this way so  that we can send this package to multiprocessor like:
    #   with Pool(n_pool) as p:
    #             b = p.starmap(do_EEA__packet, package)
    package = []
    # ccsds coarse+fine -> cdf-epoch times.
    try:
        for ptr in range(0, len(beginning_packets) + 1):
            package.append(
                (
                    l0_cdf["ACCUM"][
                        beginning_packets[ptr] : beginning_packets[ptr + 1]
                    ],  # the skymap
                    l0_cdf["COUNTER1"][
                        beginning_packets[ptr] : beginning_packets[
                            ptr + 1
                        ]  # e.g. l0_cdf["COUNTER1"][47] = 12
                    ],  # np.sum(l0_cdf["ACCUM"][47]) = 11
                    l0_cdf["COUNTER2"][
                        beginning_packets[ptr] : beginning_packets[
                            ptr + 1
                        ]  # l0_cdf["COUNTER2"][47] = 12
                    ],
                    epochs[beginning_packets[ptr] : beginning_packets[ptr + 1]],
                    step_values['energy'],  # from the stepper table
                    step_values['elevation_angle'],  # from the stepper table
                    ptr,
                )
            )
    except IndexError:
        log.info("Finished last interval")

    result = []
    for pckt in package:
        packet_contents = do_eea_packet(*pckt)
        if packet_contents is not None:
            result.append(packet_contents)
    myEEA.populate(result)


def do_eea_packet(counts, cnt1, cnt2, epoch, energy_vals, deflection_vals, ith_FSmap):
    """
    This function populates each sweep, or pass through
    all of the energies and deflections designated by the stepper table

    Parameters
    ----------
    stepperTableCounter - n_deflections * n_energies
    counts              - the structured arrays returned by CCSDSPY
    cnt1                - the sum of this sweep's accum
    cnt2                - same as above but +1...not clear yet
    epoch               - CDF Formatted time for every single measurement, [0] is the time for the sweep/packet
    energies            - so far we only have one stepper table with 41 energies
    deflections         - ...and 4 deflections
    ith_FSmap           - sweep counter

    Returns
    -------
    """
    return_package = {}
    return_package["Epoch"]  = epoch[0]     # here the "Epoch" is the traditional one: the start time of each packet
   
    return_package["usec"]   = stuff_stepsize(epoch, (MAX_STEPS), EPOCHTIMEFILL) 
    
    return_package["counts"] = np.full((MAX_STEPS, N_AZIMUTH), REAL4FILL)
    return_package["counts"][0:counts.shape[0], 0:counts.shape[1]] = counts

    #  Since we might have several different stepper tables, we aren't putting them into separate
    #  energy/deflection dimenstionxs
    return_package["energies"]    = stuff_stepsize(energy_vals, (MAX_STEPS), REAL4FILL)  # a static thing for each stepper table

    return_package["deflections"] = stuff_stepsize(deflection_vals, (MAX_STEPS), REAL4FILL)  # a static thing for each stepper table

    return_package["counter1"]    = stuff_stepsize(cnt1, (MAX_STEPS), INTFILL)         # number of counts in each packet (not each sweep)

    return_package["counter2"]    = stuff_stepsize(cnt2, (MAX_STEPS), INTFILL)         # number of counts in each packet

    return return_package


def manage_stepper_table_energies_and_angles(beginning_packets, stepper, packet, npackets):
    """
    I'm doing it this way mostly to be able to handle the last,
    incomplete sweep"""

    stepvalues = {}
    stepvalues['energy'] = []
    stepvalues['elevation_angle'] = []
    finish = npackets
    try:
        if beginning_packets[packet + 1]:
            finish = beginning_packets[packet+1]
    except TypeError:
        pass  # we are in last incomplete packet
     
    for i in range(beginning_packets[packet], finish):
        
        stepvalues['energy'].append(stepper.v_energies[stepper.energies[i]])
        stepvalues['elevation_angle'].append(stepper.v_defl[stepper.deflections[i]])
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

    