"""
A module for all things calibration.
"""
from datetime import datetime, timezone, timedelta
import random
import os.path
from pathlib import Path
import sys
import ccsdspy
import numpy as np

from hermes_core import log
from hermes_core.util.util import create_science_filename, parse_science_filename
import hermes_eea
from hermes_eea.io import read_file
import hermes_eea.calibration as calib
from hermes_eea.io.EEA import EEA
from hermes_eea.SkymapFactory import SkymapFactory
from hermes_eea.util.time.iso_epoch import (
    epoch_to_iso_obj,
    epoch_to_eea_iso,
    epoch_to_iso,
)
from spacepy import pycdf

from hermes_eea.calibration.build_spectra import Hermes_EEA_Data_Processor

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
    for filename in data_filename:
        calibrated_file = calibrate_file(filename)
        output_files.append(calibrated_file)
        #  data_plot_files = plot_file(data_filename)
        #  calib_plot_files = plot_file(calibrated_file)

    # add other tasks below
    return output_files


def calibrate_file(data_filename: Path, destination_dir) -> Path:
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
    if not destination_dir.is_dir():
        raise OSError(
            "Output directory: " + str(destination_dir) + ". Please create first."
        )
        return
    output_filename = (
        data_filename  # TODO: for testing, the output filename MUST NOT same as input
    )
    file_metadata = parse_science_filename(data_filename.name)

    # check if level 0 binary file, if so call appropriate functions
    if (
        file_metadata["instrument"] == hermes_eea.INST_NAME
        and file_metadata["level"] == "l0"
    ):
        # because of error handling, no test of data is necessary here.
        data = parse_l0_sci_packets(data_filename)
        level1_filename = l0_sci_data_to_cdf(data, data_filename, destination_dir)
        output_filename = level1_filename
    elif (
        file_metadata["instrument"] == hermes_eea.INST_NAME
        and file_metadata["level"] == "l1"
    ):
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
        # here
        data = parse_l0_sci_packets(data_filename)
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


def l0_sci_data_to_cdf(
    data: dict, original_filename: Path, destination_dir: Path
) -> Path:
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

    # this is transferring name.bin to name.cdf
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
        try:
            cdf = pycdf.CDF(
                str(cdf_filename),
                os.path.join(
                    hermes_eea._data_directory,
                    "masterSkeletons/hermes_eea_l1_00000000000000_v0.0.0.cdf",
                ),
            )
            cdf.close()
        except FileNotFoundError:
            pass
    if data:
        # cdf = pycdf.CDF(str(cdf_filename))
        # cdf.readonly(False)

        calibration_file = get_calibration_file(hermes_eea.stepper_table)
        read_calibration_file(calibration_file)

        myEEA = EEA(file_metadata)
        # This populates so doesn't have to return much
        SkymapFactory(data, calib.energies, calib.deflections, myEEA)
        most_active = np.where(np.array(myEEA.stats) > 150)
        example_start_times = epoch_to_iso_obj(myEEA.Epoch[0:10])

        n_packets = len(myEEA.Epoch)

        hermes_eea_factory = Hermes_EEA_Data_Processor(myEEA)
        hermes_eea_factory.build_HermesData()

        try:
            cdf_path = hermes_eea_factory.hermes_eea_data.save(
                str(destination_dir), True
            )
        except Exception as e:
            log.error(e)
            sys.exit(2)

    return cdf_path


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
    return os.path.join(hermes_eea._calibration_directory, data_filename)


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
    lines = read_file(os.path.join(calib_filename))
    calib.energies = []
    calib.deflections = []
    for line in lines:
        calib.energies.append(int(line[8:10], 16))
        calib.deflections.append(int(line[10:12], 16))


def retrieve_canned_attributes():
    input_attrs = {
        "DOI": "https://doi.org/<PREFIX>/<SUFFIX>",
        "Data_level": "L1>Level 1",  # NOT AN ISTP ATTR
        "Data_version": "0.0.1",
        "Descriptor": "EEA>Electron Electrostatic Analyzer",
        "Data_product_descriptor": "odpd",
        "HTTP_LINK": [
            "https://spdf.gsfc.nasa.gov/istp_guide/istp_guide.html",
            "https://spdf.gsfc.nasa.gov/istp_guide/gattributes.html",
            "https://spdf.gsfc.nasa.gov/istp_guide/vattributes.html",
        ],
        "Instrument_mode": "default",  # NOT AN ISTP ATTR
        "Instrument_type": "Electric Fields (space)",
        "LINK_TEXT": ["ISTP Guide", "Global Attrs", "Variable Attrs"],
        "LINK_TITLE": ["ISTP Guide", "Global Attrs", "Variable Attrs"],
        "MODS": [
            "v0.0.0 - Original version.",
            "v1.0.0 - Include trajectory vectors and optics state.",
            "v1.1.0 - Update metadata: counts -> flux.",
            "v1.2.0 - Added flux error.",
            "v1.3.0 - Trajectory vector errors are now deltas.",
        ],
        "PI_affiliation": "HERMES",
        "PI_name": "HERMES SOC",
        "TEXT": "Valid Test Case",
        "VATTRS": ["stats", "energies"],
    }

    return input_attrs
