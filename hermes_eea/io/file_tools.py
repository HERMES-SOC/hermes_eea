from ccsdspy import FixedLength
import numpy as np

"""
This module provides a generic file reader.
"""

__all__ = ["read_file"]


def read_file(data_filename):
    """
    Read a file.

    Parameters
    ----------
    data_filename: str
        A file to read.

    Returns
    -------
    data: str

    Examples
    --------
    """
    return None


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


def unbin_field(field_bin: np.bytes_, bin_cnt: int, bin_size: int):
    """
    Unbin arrays from a packet field.

    Parameters
    ----------
    field_bin: `np.bytes_`
        bytes representation of the field to unbin.

    bin_cnt:
        Number of bins in the field.

    bin_size:
        Length of each bin in the field.

    Returns
    -------
    list: List of ints in the array field.
    """
    mask = 2**bin_size - 1
    unbinned = np.zeros(bin_cnt, dtype=int)
    for bin in range(bin_cnt):
        shift_size = bin_size * (bin_cnt - bin) - bin_size
        bin_data = (int.from_bytes(field_bin, "big") >> shift_size) & mask
        unbinned[bin] = bin_data
    return unbinned
