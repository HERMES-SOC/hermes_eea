from pathlib import Path
from ccsdspy import FixedLength
import numpy as np

"""
This module provides a generic file reader.
"""

__all__ = ["read_file", "read_ccsds"]


def read_file(data_filename: Path):
    """
    Read a file.

    Parameters
    ----------
    data_filename: `pathlib.Path`
        A file to read.

    Returns
    -------
    data: str

    Examples
    --------
    """
    try:
        with open(data_filename) as fh:
            return fh.readlines()
    except Exception:
        raise Exception("Could not find: " + data_filename)


def read_ccsds(filename: Path, pkt_def: FixedLength):
    """
    Read a ccsds packet file.

    Parameters
    ----------
    filename: `pathlib.Path`
        A file to read.

    pkt_def: `ccsdspy.FixedLength`
        CCSDS packet definition

    Returns
    -------
    `OrderedDict` mapping field names to NumPy arrays.
    """
    result = pkt_def.load(filename)
    return result
