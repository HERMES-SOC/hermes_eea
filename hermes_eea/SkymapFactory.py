import numpy as np
from hermes_core import log
from hermes_eea.io import EEA
from hermes_eea.util.time import ccsds_to_cdf_time
from hermes_eea import energies as voltages

N_ENERGIES = 41
N_DEFLECTIONS = 4
N_AZIMUTH = 32


# This may eventually be handled in a python multiprocessor module instance:
def SkymapFactory(l0_cdf, energies, deflections, myEEA):
    # ['Epoch', 'Epoch_plus_var', 'Epoch_minus_var', 'hermes_eea_step_counter',
    # 'hermes_eea_counter1', 'hermes_eea_counter2', 'hermes_eea_accumulations',
    # 'hermes_eea_sector_index', 'hermes_eea_sector_label'])

    # science_data:
    start_of_good_data = np.where(l0_cdf["SHEID"][:] == 1)[0][0]
    integrates_at_end = np.where(
        l0_cdf["SHEID"][start_of_good_data:] == 0
    )  # has 63 values
    # We are expecting integrates to be only at the beginning

    # The Science Data:
    stepper_table_packets = (np.where(l0_cdf["SHEID"][:] > 0))[0]
    return_package = {}
    beginning_packets = (
        np.where((l0_cdf["STEP"][stepper_table_packets[0] :]) == 0)[0]
        + stepper_table_packets[0]
    )
    package = []

    epochs = ccsds_to_cdf_time.helpConvertEEA(l0_cdf)
    try:
        for ptr in range(0, len(beginning_packets)):
            package.append(
                (
                    l0_cdf["STEP"][beginning_packets[ptr] : beginning_packets[ptr + 1]],
                    l0_cdf["ACCUM"][
                        beginning_packets[ptr] : beginning_packets[ptr + 1]
                    ],
                    l0_cdf["COUNTER1"][
                        beginning_packets[ptr] : beginning_packets[ptr + 1]
                    ],
                    l0_cdf["COUNTER2"][
                        beginning_packets[ptr] : beginning_packets[ptr + 1]
                    ],
                    epochs[beginning_packets[ptr] : beginning_packets[ptr + 1]],
                    energies,
                    deflections,
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
    myEEA.populate(myEEA, result)


def do_eea_packet(
    stepperTableCounter, counts, cnt1, cnt2, epoch, energies, deflections, ith_FSmap
):
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
    rows = len(stepperTableCounter)
    # skymap is already full of zeros, why do it again?
    # skymap = np.zeros((beginning_packets[ptr+1]-beginning_packets[ptr],N_AZIMUTH))
    skymaps = []
    pulse_a = np.zeros((N_ENERGIES, N_DEFLECTIONS), dtype=np.uint16)
    pulse_b = np.zeros((N_ENERGIES, N_DEFLECTIONS), dtype=np.uint16)
    counter1 = np.zeros((N_ENERGIES, N_DEFLECTIONS), dtype=np.uint16)
    counter2 = np.zeros((N_ENERGIES, N_DEFLECTIONS), dtype=np.uint16)
    usec = np.zeros((N_ENERGIES, N_DEFLECTIONS), dtype=np.uint16)

    skymap = np.zeros((N_ENERGIES, N_DEFLECTIONS, N_AZIMUTH), dtype=np.uint16)

    for row in stepperTableCounter:
        dim0 = energies[row]
        dim1 = deflections[row]
        skymap[dim0, dim1, :] = counts[row, 0:N_AZIMUTH]
        pulse_a[dim0, dim1] = counts[row][N_AZIMUTH]
        pulse_b[dim0, dim1] = counts[row][N_AZIMUTH + 1]
        counter1[dim0, dim1] = cnt1[row]
        counter2[dim0, dim1] = cnt2[row]
        usec[dim0, dim1] = epoch[row]

    return_package["pulse_a"] = pulse_a
    return_package["pulse_b"] = list(pulse_b)
    return_package["counts"] = skymap
    return_package["usec"] = usec
    return_package["Epoch"] = epoch[0]
    return_package["stats"] = np.sum(skymap)
    return_package["energies"] = voltages
    return_package["sun_angles"] = deflections
    return_package["counter1"] = counter1
    return_package["counter2"] = counter2

    return return_package
