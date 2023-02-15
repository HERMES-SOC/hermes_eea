"""
A module for all things calibration.
"""
from datetime import datetime, timezone, timedelta
import random
import os.path
from pathlib import Path

import ccsdspy
import numpy as np
from spacepy import pycdf

from hermes_core import log
from hermes_core.util.util import create_science_filename, parse_science_filename

import hermes_eea
from hermes_eea.io import read_file

__all__ = [
    "process_file",
    "parse_l0_sci_packets",
    "l0_sci_data_to_cdf",
    "calibrate_file",
    "get_calibration_file",
    "read_calibration_file",
]


def process_file(data_filename: Path) -> list:
    """
    This is the entry point for the pipeline processing.
    It runs all of the various processing steps required.

    Parameters
    ----------
    data_filename: str
        Fully specificied filename of an input file

    Returns
    -------
    output_filenames: list
        Fully specificied filenames for the output files.
    """
    log.info(f"Processing file {data_filename}.")
    output_files = []

    calibrated_file = calibrate_file(data_filename)
    output_files.append(calibrated_file)
    #  data_plot_files = plot_file(data_filename)
    #  calib_plot_files = plot_file(calibrated_file)

    # add other tasks below
    return output_files


def calibrate_file(data_filename: Path) -> Path:
    """
    Given an input data file, raise it to the next level
    (e.g. level 0 to level 1, level 1 to quicklook) it and return a new file.

    Parameters
    ----------
    data_filename: Path
        Fully specificied filename of the input data file.

    Returns
    -------
    output_filename: Path
        Fully specificied filename of the output file.

    Examples
    --------
    >>> from hermes_eea.calibration import calibrate_file
    >>> level1_file = calibrate_file('hermes_EEA_l0_2022239-000000_v0.bin')  # doctest: +SKIP
    """
    log.info(f"Calibrating file:{data_filename}.")
    output_filename = data_filename  # TODO: for testing, the output filename MUST NOT same as input
    file_metadata = parse_science_filename(data_filename.name)

    # check if level 0 binary file, if so call appropriate functions
    if file_metadata["instrument"] == hermes_eea.INST_NAME and file_metadata["level"] == "l0":
        data = parse_l0_sci_packets(data_filename)

        level1_filename = l0_sci_data_to_cdf(data, data_filename)
        output_filename = level1_filename
    elif file_metadata["instrument"] == hermes_eea.INST_NAME and file_metadata["level"] == "l1":
        # generate the quicklook data
        #
        # the following shows an example flow for calibrating a file
        # data = read_file(data_filename)
        # calib_file = get_calibration_file(data_filename)
        # if calib_file is None:
        #    raise ValueError(f"Calibration file for {data_filename} not found.")
        # else:
        #    calib_data = read_calibration_file(calib_file)

        # test opening the file
        with open(data_filename, "r") as fp:
            pass

        # now that you have your calibration data, you can calibrate the science data
        ql_filename = data_filename.parent / create_science_filename(
            file_metadata["instrument"],
            file_metadata["time"],
            "ql",
            file_metadata["version"],
        )

        # write your cdf file below
        # create an empty file for testing purposes
        with open(data_filename.parent / ql_filename, "w"):
            pass

        # example log messages
        log.info(f"Despiking removing {random.randint(0, 10)} spikes")
        log.warning(f"Despiking could not remove {random.randint(1, 5)}")
        output_filename = ql_filename
    else:
        raise ValueError(f"The file {data_filename} is not recognized.")

    return output_filename


def parse_l0_sci_packets(data_filename: Path) -> dict:
    """
    Parse a level 0 eea binary file containing CCSDS packets.

    Parameters
    ----------
    data_filename: str
        Fully specificied filename

    Returns
    -------
    result: dict
        A dictionary of arrays which includes the ccsds header fields

    Examples
    --------
    >>> import hermes_eea.calibration as calib
    >>> data_filename = "hermes_EEA_l0_2022339-000000_v0.bin"
    >>> data = calib.parse_eea_sci_packets(data_filename)  # doctest: +SKIP
    """
    log.info(f"Parsing packets from file:{data_filename}.")

    pkt = ccsdspy.FixedLength.from_file(
        os.path.join(hermes_eea._data_directory, "hermes_EEA_sci_packet_def.csv")
    )
    data = pkt.load(data_filename)
    return data


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


def l0_sci_data_to_cdf(data: dict, original_filename: Path) -> Path:
    """
    Write level 0 eea science data to a level 1 cdf file.

    Parameters
    ----------
    data: dict
        A dictionary of arrays which includes the ccsds header fields
    original_filename: Path
        The Path to the originating file.

    Returns
    -------
    output_filename: Path
        Fully specificied filename of cdf file

    Examples
    --------
    >>> from pathlib import Path
    >>> from hermes_core.util.util import parse_science_filename
    >>> import hermes_eea.calibration as calib
    >>> data_filename = Path("hermes_EEA_l0_2022339-000000_v0.bin")
    >>> metadata = parse_science_filename(data_filename)  # doctest: +SKIP
    >>> data_packets = calib.parse_l0_sci_packets(data_filename)  # doctest: +SKIP
    >>> cdf_filename = calib.l0_sci_data_to_cdf(data_packets, data_filename)  # doctest: +SKIP
    """
    file_metadata = parse_science_filename(original_filename.name)

    # coarse = data["SHCOARSE"][idx]
    # fine = data["SHFINE"][idx]
    # time = convert_packet_time_to_datetime(coarse, fine)
    cdf_filename = original_filename.parent / create_science_filename(
        file_metadata["instrument"],
        file_metadata["time"],
        "l1",
        f'1.0.{file_metadata["version"]}',
    )
    if not cdf_filename.is_file():
        cdf = pycdf.CDF(
            str(cdf_filename),
            os.path.join(
                hermes_eea._data_directory,
                "masterSkeletons/hermes_eea_l1_00000000000000_v0.0.0.cdf",
            ),
        )
        cdf["Epoch"] = converting_ccsds_times_to_cdf(data["SHCOARSE"], data["SHFINE"])
        cdf["hermes_eea_accumulations"] = data["ACCUM"]
        cdf["hermes_eea_counter1"] = data["COUNTER1"]
        cdf["hermes_eea_counter2"] = data["COUNTER2"]
        cdf["hermes_eea_step_counter"] = data["STEP"]

        cdf.close()

    return cdf_filename


def get_calibration_file(data_filename: Path, time=None) -> Path:
    """
    Given a time, return the appropriate calibration file.

    Parameters
    ----------
    data_filename: str
        Fully specificied filename of the non-calibrated file (data level < 2)
    time: ~astropy.time.Time

    Returns
    -------
    calib_filename: str
        Fully specificied filename for the appropriate calibration file.

    Examples
    --------
    """
    return None


def read_calibration_file(calib_filename: Path):
    """
    Given a calibration, return the calibration structure.

    Parameters
    ----------
    calib_filename: str
        Fully specificied filename of the non-calibrated file (data level < 2)

    Returns
    -------
    output_filename: str
        Fully specificied filename of the appropriate calibration file.

    Examples
    --------
    """
    return None
