import numpy as np
from hermes_core import log
from hermes_eea.io import EEA
from hermes_eea.util.time import ccsds_to_cdf_time
from hermes_eea import energies as voltages

N_ENERGIES = 41
N_DEFLECTIONS = 4
N_AZIMUTH = 34


def SkymapFactory(l0_cdf, energies, deflections, myEEA):
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

    # This is done this way so  that we can send this package to multiprocessor like:
    #   with Pool(n_pool) as p:
    #             b = p.starmap(do_EEA__packet, package)
    package = []
    # ccsds coarse+fine -> cdf-epoch times.
    epochs = ccsds_to_cdf_time.help_convert_eaa(l0_cdf)
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
                    energies,  # from the stepper table
                    deflections,  # from the stepper table
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


def do_eea_packet(counts, cnt1, cnt2, epoch, energies, deflections, ith_FSmap):
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

    #  Since we might have several different stepper tables, we aren't putting them into separate
    #  energy/deflection dimenstionxs
    return_package["counts"]     = counts
    return_package["usec"]       = epoch        # we call this µsec, because it is the time of each step in the sweep within each packet.
    return_package["Epoch"]      = epoch[0]     # here the "Epoch" is the traditional one: the start time of each packet
    return_package["energies"]   = voltages     # a static thing for each stepper table
    return_package["sun_angles"] = deflections  # a static thing for each stepper table I think this is supposed to be angles, not 0,1,2,3 get from Skeberdis
    return_package["counter1"]   = cnt1         # number of counts in each packet
    return_package["counter2"]   = cnt2         # number of counts in each packet.

    return return_package
