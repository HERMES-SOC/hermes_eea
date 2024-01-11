"""Utils for the CCSDSPy package."""

__author__ = "Richard Strub <richard.f.strub@nasa.gov>"

import numpy as np


def helpConvertEEA(decoded):
    coarse = np.uint(decoded["SHCOARSE"])
    fine = np.uint(decoded["SHFINE"])
    epoch = converting_ccsds_times_to_cdf(coarse, fine)
    return epoch


def converting_ccsds_times_to_cdf(coarse, fine):
    epoch = np.zeros(coarse.shape[0], dtype=np.uint)
    p1 = np.zeros(coarse.shape[0], dtype=np.uint)
    p2 = np.zeros(coarse.shape[0], dtype=np.uint)

    tai_time = {}
    # FPI:
    # tai_time["taiEpoch_tt2000"] = 1325419167816000000
    # EEA:
    tai_time["taiEpoch_tt2000"] = -64184000000
    tai_time["nanosPerMicro"] = 1000
    tai_time["MicrosPerSec"] = 1000000
    tai_time["nanosPerSec"] = 1000000000

    example = coarse[0] * tai_time["nanosPerSec"]
    p1 = np.int64(coarse) * np.int64(tai_time["nanosPerSec"])
    p2 = np.int64(fine) * np.int64(tai_time["nanosPerMicro"])
    epoch = p1 + p2
    result = np.uint64(epoch - tai_time["taiEpoch_tt2000"])
    return result
