"""Utils for the CCSDSPy package."""

__author__ = "Richard Strub <richard.f.strub@nasa.gov>"

import numpy as np


def help_convert_eaa(decoded) -> np.ndarray:
    """

    Parameters
    ----------
    decoded - this is the binary packets parsed by CCSDSPY using
    config file: hermes_EEA_sci_packet_def.csv. Arrays usually include
    APID, then a COARSE and FINE time that we translate into CDF EPOCH
    according to examples in original IDL FPI Ground System code.

    Returns
    -------
    Integer time. Something we think of as CDF EPOCH time that is fairly
    easy to then convert  int o ISO.

    """
    coarse = np.uint(decoded["SHCOARSE"])
    fine = np.uint(decoded["SHFINE"])
    epoch = converting_ccsds_times_to_cdf(coarse, fine)
    return epoch


def converting_ccsds_times_to_cdf(coarse, fine):
    """
    Parameters
    ----------
    coarse - CCSDSPY time parm
    fine     CCSDSPY time parm
    CCSDS telemetry files often include this COARSE and FINE times
    that we translate into CDF EPOCH according to examples in original
    IDL FPI Ground System code.

    Returns
    -------
    CDF-EPOCH time. Number of millisecs since 0 AD.
    tai_time["taiEpoch_tt2000"] for FPI was different than for EEA.
    I am not sure if this was chosen arbitrarily or through direction from Hermes SOC
    """
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
