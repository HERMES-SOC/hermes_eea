"""Utils for the CCSDSPy package."""

__author__ = "Richard Strub <richard.f.strub@nasa.gov>"

import numpy as np


def helpConvert(decoded):
    coarse = np.uint(decoded["START_CORSTIME"])
    fine = np.uint(decoded["START_FINETIME"])
    epoch = converting_ccsds_times_to_cdf(coarse, fine)
    return epoch

def helpConvertEEA(decoded):
    coarse = np.uint(decoded["SHCOARSE"])
    fine = np.uint(decoded["SHFINE"])
    epoch = converting_ccsds_times_to_cdf(coarse, fine)
    return epoch

def helpConvertMagFld(decoded):
    coarse = np.uint(decoded["MAGMSGCOARSETM"])
    fine = np.uint(decoded["MAGMSGFINETIME"])
    epoch = converting_ccsds_times_to_cdf(coarse, fine)
    return epoch



def converting_ccsds_times_to_cdf(coarse, fine):

    epoch = np.zeros(coarse.shape[0], dtype=np.uint)
    p1 = np.zeros(coarse.shape[0], dtype=np.uint)
    p2 = np.zeros(coarse.shape[0], dtype=np.uint)

    tai_time = {}
    tai_time["taiEpoch_tt2000"] = 1325419167816000000
    tai_time["nanosPerMicro"] = 1000
    tai_time["MicrosPerSec"] = 1000000
    tai_time["nanosPerSec"] = 1000000000

    example = coarse[0] * tai_time["nanosPerSec"]
    p1 = np.int64(coarse) * np.int64(tai_time["nanosPerSec"])
    p2 = np.int64(fine) * np.int64(tai_time["nanosPerMicro"])
    epoch = p1 + p2
    result = np.uint(epoch - tai_time["taiEpoch_tt2000"])
    return result

def reverse_cnv_cdf_times_to_ccsds(epoch):

    tai_time = {}
    tai_time["taiEpoch_tt2000"] = 1325419167816000000
    tai_time["nanosPerMicro"] = 1000
    tai_time["MicrosPerSec"] = 1000000
    tai_time["nanosPerSec"] = 1000000000
    TAI_us = int((epoch + tai_time["taiEpoch_tt2000"]) / tai_time["nanosPerMicro"])

    coarse = int(TAI_us  / tai_time["MicrosPerSec"]) #; CCSDS sec
    fine = TAI_us % tai_time["MicrosPerSec"] #; CCSDS us
    return (coarse, fine)

def calc_Epoch_for_Trigger(raw_data):
    '''
    I'm not at all sure what this is all about...How is this result different from the usual
    PODA to CDF conversion?
    :param raw_data:
    :return:
    '''
    Timeus = {}
    Timeus["288"] = 30000
    Timeus["296"] = 150000
    thisTimeus = Timeus[str(raw_data["PREPENDED_APID"][0])]

    usPerSec = 1000000
    elePerSamp = (raw_data["CMPTRIGGERTERM"]).shape[1] # 288 = 150 , 296 = 30
    nDes = len(raw_data["PREPENDED_APID"])
    corsTime = np.zeros(nDes * elePerSamp, "u4")
    fineTime = np.zeros(nDes * elePerSamp, "u4")
    for i in range(0, nDes):
        startusec = raw_data["START_CORSTIME"][i] * usPerSec + raw_data["START_FINETIME"][i]
        stop = (elePerSamp * thisTimeus) + startusec
        usecs = np.arange(startusec, stop, thisTimeus)
        offset = i * elePerSamp
        corsTime[offset:offset + elePerSamp] = usecs / usPerSec
        fineTime[offset:offset + elePerSamp] = usecs % usPerSec

    new_Epoch = converting_ccsds_times_to_cdf(corsTime, fineTime )
    return new_Epoch