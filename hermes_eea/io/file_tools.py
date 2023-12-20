from ccsdspy import FixedLength
import numpy as np

"""
This module provides a generic file reader.
"""
import os.path
from pathlib import Path

import ccsdspy

from hermes_core.util.util import create_science_filename, parse_science_filename
from hermes_core.timedata import HermesData
from hermes_core.util.validation import validate

from hermes_eea import log
import hermes_eea

__all__ = [
    "load_data_file",
    "parse_l0_sci_packets",
    "read_calibration_file",
    "write_data_file",
]


def load_data_file(data_filename: Path) -> HermesData:
    """
    Given an input file, load the file's data from a physical file data format
    to a logical data format that can be used for calibration and analysis.

    Parameters
    ----------
    data_filename: Path
        Fully specificied filename of the input data file.

    Returns
    -------
    instrument_data: HermesData
        A data container in a logical data format for loading, storing, and manipulating
        HERMES time series data

    Examples
    --------
    """
    log.info(f"Loading Data File: {data_filename}.")

    # Get Filename Information
    file_metadata = parse_science_filename(data_filename.name)

    # check if level 0 binary file, if so call appropriate functions
    if file_metadata["level"] == "l0":
        instrument_data = parse_l0_sci_packets(data_filename)
    # If not level 0 binary file, load as a CDF file
    else:
        # As an example, you can load CDF files directly into the data container
        instrument_data = HermesData.load(str(data_filename))

    return instrument_data


def parse_l0_sci_packets(data_filename: Path) -> HermesData:
    """
    Parse a level 0 eea binary file containing CCSDS packets.

    Parameters
    ----------
    data_filename: str
        Fully specificied filename of l0 packet file

    Returns
    -------
    instrument_data: HermesData
        A data container in a logical data format containing the l0 data

    Examples
    --------
    >>> import hermes_eea.calibration as calib
    >>> data_filename = "hermes_EEA_l0_2022339-000000_v0.bin"
    >>> data = calib.parse_l0_sci_packets(data_filename)  # doctest: +SKIP
    """
    log.info(f"Parsing packets from file:{data_filename}.")

    try:
        pkt = ccsdspy.FixedLength.from_file(
            os.path.join(hermes_eea._data_directory, "EEA_sci_packet_def.csv")
        )
        data = pkt.load(data_filename)
    except (RuntimeError, ValueError, KeyError):
        log.critical(f"Failed to Parse Packets for file:{data_filename}.")
        raise RuntimeError(
            f"Failed to Parse Packets for file:{data_filename}. Please ensure Packet Definition: EEA_sci_packet_def.csv is correct."
        )

    # Process the Packet dict to create a HermesData data container
    # NOTE: Template does no transormations here.
    instrument_data = None

    return instrument_data


def read_calibration_file(calib_filename: Path) -> Path:
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
    try:
        with open(data_filename) as fh:
            return fh.readlines()
    except Exception:
        raise Exception("Could not find: " + data_filename)


def read_ccsds(filename: str, pkt_def: FixedLength):
    """
    Read a ccsds packet file.

    Parameters
    ----------
    filename: str
        A file to read.

    pkt_def: `ccsdspy.FixedLength`
        CCSDS packet definition

    Returns
    -------
    `OrderedDict` mapping field names to NumPy arrays.
    """
    result = pkt_def.load(filename)
    return result
