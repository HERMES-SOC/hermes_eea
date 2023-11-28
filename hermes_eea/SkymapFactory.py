
import numpy as np
from hermes_core import log
from hermes_eea.io import EEA
from hermes_eea.util.time import ccsds_to_cdf_time


# This may eventually be put inside a multiprocessor:
def SkymapFactory(l0_cdf,energies,deflections,myEEA):
    #['Epoch', 'Epoch_plus_var', 'Epoch_minus_var', 'hermes_eea_step_counter',
    #'hermes_eea_counter1', 'hermes_eea_counter2', 'hermes_eea_accumulations',
    #'hermes_eea_sector_index', 'hermes_eea_sector_label'])

    # science_data:
    start_of_good_data = np.where(l0_cdf['SHEID'][:] == 1)[0][0]
    integrates_at_end = np.where(l0_cdf['SHEID'][start_of_good_data:] == 0) # has 63 values
    # We are expecting integrates to be only at the beginning

    # The Science Data:
    stepper_table_packets = (np.where(l0_cdf['SHEID'][:] > 0))[0]
    return_package = {}
    beginning_packets = np.where((l0_cdf['STEP'][stepper_table_packets[0]:]) == 0 )[0] + stepper_table_packets[0]
    package = []

    epochs = ccsds_to_cdf_time.helpConvertEEA(l0_cdf)
    try:
        #for ptr in range(0,len(beginning_packets)):
        for ptr in range(0,2000):
            #skymap = np.zeros((beginning_packets[ptr+1]-beginning_packets[ptr],32))
            package.append((
                l0_cdf['STEP'][beginning_packets[ptr]:beginning_packets[ptr+1]],
                l0_cdf['ACCUM'][beginning_packets[ptr]:beginning_packets[ptr+1]],
                l0_cdf['COUNTER1'][beginning_packets[ptr]:beginning_packets[ptr+1]],
                l0_cdf['COUNTER2'][beginning_packets[ptr]:beginning_packets[ptr+1]],
                epochs[beginning_packets[ptr]:beginning_packets[ptr+1]],

                energies, deflections,ptr
            ))
    except IndexError:
        log.info("Finished last interval")

    result = []
    for pckt in package:
                packet_contents = do_eea_packet(*pckt)
                if packet_contents != None:
                   result.append(packet_contents)
    myEEA.populate(myEEA, result)

    #epoch = ccsds_to_cdf_time.helpConvert_eea(l0_cdf)
    #zero_values_past_first = np.where(l0_cdf['hermes_eea_intgr_or_stepper'][135:] == 0)[0]
    #l0_cdf['hermes_eea_step_counter'][zero_values_past_first]
    #first_packages = np.where(l0_cdf['SHEID'] > 0)

# This does an entire sweep of, nominally, 164 thingies
def do_eea_packet( stepperTableCounter,
                   counts,
                   cnt1,cnt2,
                   epoch,
                   energies,
                   deflections,ith_FSmap):

     return_package = {}
     rows = len(stepperTableCounter)
     # skymap is already full of zeros, why do it again?
     # skymap = np.zeros((beginning_packets[ptr+1]-beginning_packets[ptr],32))
     skymaps = []
     pulse_a = np.zeros((41,4), dtype=np.uint16)
     pulse_b = np.zeros((41,4), dtype=np.uint16)
     counter1 = np.zeros((41,4), dtype=np.uint16)
     counter2 = np.zeros((41,4), dtype=np.uint16)
     µepoch   = np.zeros((41,4), dtype=np.uint16)

     skymap = np.zeros((41, 4, 32), dtype=np.uint16)

     for row in stepperTableCounter:
         dim0 = energies[row]
         dim1 = deflections[row]
         if cnt1[row] > 3:
             pass
         skymap[dim0, dim1, :]     = counts[row,0:32]
         pulse_a[dim0, dim1] = counts[row][32]
         pulse_b[dim0, dim1] = counts[row][33]
         counter1[dim0, dim1] = cnt1[row]
         counter2[dim0, dim1] = cnt2[row]
         µepoch[dim0, dim1] = epoch[row]


# if len(stepperTableCounter) != 64:
    #    log.info(str(ith_FSmap) + ": stepperTable rows:" + str(len(stepperTableCounter)))
    #    return None
     return_package['pulse_a'] = pulse_a
     return_package['pulse_b'] = list(pulse_b)
     return_package['counts']  = skymap
     return_package['µEpoch']  = µepoch
     return_package['Epoch']  =  epoch[0]
     return_package['stats']  =  np.sum(skymap)
     return_package['energies']  =  energies
     return_package['sun_angles']  = deflections
     return_package['counter1'] = counter1
     return_package['counter2'] = counter2

     return return_package


