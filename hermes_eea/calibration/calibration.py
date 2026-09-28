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
import astropy.units as astropy_units
from astropy.timeseries import TimeSeries

from hermes_core import log
from hermes_core.util.util import create_science_filename, parse_science_filename
from hermes_core.timedata import HermesData
import hermes_eea
from hermes_eea.io import read_file
import hermes_eea.calibration as calib
from hermes_eea.io.EEA import EEA
from hermes_eea.SkymapFactory import skymap_factory
from hermes_eea.Stepper.StepperTable import StepperTable
from hermes_eea.util.time import ccsds_to_cdf_time

# cdflib -> spacepy
from spacepy.pycdf import lib
from hermes_eea.calibration.build_spectra import Hermes_EEA_Data_Processor
from astropy.time import Time

__all__ = [
    "process_file",
    "parse_l0_sci_packets",
    "parse_hk_packets",
    "l0_sci_data_to_cdf",
    "l0_hk_data_to_cdf",
    "calibrate_file",
    "get_calibration_file",
    "read_calibration_file",
]


def process_file(data_filename: Path, stepper: StepperTable = None, apid: int = None) -> list:
    """
    This is the entry point for the pipeline processing.
    It runs all of the various processing steps required
    to create a L1A Hermes CDF File
    calls:
        calibrate_file()
           parse_science
           CCSDSPY (parse_L0_sci_packets())
           l0_sci_data_to_cdf()
                SkymapFactory()
                Use HermesData to populate CDF output file
                Write the File
        A Custom EEA SkymapFactory
        HermesData

    Parameters
    ----------
    data_filename: str
        Fully specificied filename of an input file.
        The file contents:
            Traditional binary packets in CCSDS format


    Returns
    -------
    output_filenames: list
        Fully specificied filenames for the output files.
    The file contents:
        CDF formatted file with n packets iincluding time and [41,4,32] skymap.
    """
    log.info(f"Processing file {data_filename}.")
    output_files = []

    # Get the Directory of the File
    destination_dir = data_filename.parent

    # Calibrate the Input File
    calibrated_file = calibrate_file(data_filename, destination_dir, stepper, apid)
    output_files.append(calibrated_file)

    # Add Plots to the Output Files if we want
    #  data_plot_files = plot_file(data_filename)
    #  calib_plot_files = plot_file(calibrated_file)

    # add other tasks below
    return output_files


def calibrate_file(data_filename: Path, destination_dir, stepper: StepperTable = None, apid: int = None) -> Path:
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

    """
    log.info(f"Calibrating file:{data_filename}.")
    # stepper = StepperTable(hermes_eea.stepper_table)
  
    file_metadata = parse_science_filename(data_filename.name)
    
    # check if level 0 binary file, if so call appropriate functions
    if (
        file_metadata["instrument"] == hermes_eea.INST_NAME
        and apid == 260
    ):
        if stepper is None:
            log.info(f"No StepperTable provided for level-0 science file {data_filename}.")
            pass
          
        # call CCSDSPY to parse our packets.
        data = parse_l0_sci_packets(data_filename)
        level1_filename = l0_sci_data_to_cdf(stepper, data, data_filename, destination_dir)
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
    elif apid == 265:
        log.info(f"Processing HK file: {data_filename}.")
        data = parse_hk_packets(data_filename)
        output_filename = l0_hk_data_to_cdf(data, data_filename, destination_dir)
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
    data = pkt.load(data_filename, include_primary_header=True)

    unique_apids = sorted(set(data["CCSDS_APID"].tolist()))
    log.info(f"Parsed APID(s): {unique_apids}")

    # drop the primary header fields, callers only expect the science fields
    for header_field in (
        "CCSDS_VERSION_NUMBER",
        "CCSDS_PACKET_TYPE",
        "CCSDS_SECONDARY_FLAG",
        "CCSDS_SEQUENCE_FLAG",
        "CCSDS_APID",
        "CCSDS_SEQUENCE_COUNT",
        "CCSDS_PACKET_LENGTH",
    ):
        data.pop(header_field, None)

    return data


def parse_hk_packets(data_filename: Path) -> dict:
    """
    Parse a level 0 eea housekeeping binary file containing CCSDS packets.

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
    >>> data_filename = "hermes_EEA_hk_l0_2022339-000000_v0.bin"
    >>> data = calib.parse_hk_packets(data_filename)  # doctest: +SKIP
    """
    log.info(f"Parsing HK packets from file:{data_filename}.")

    pkt = ccsdspy.FixedLength.from_file(
        os.path.join(hermes_eea._data_directory, "hermes_EEA_hk_packet_def.csv")
    )
    data = pkt.load(data_filename, include_primary_header=True)

    unique_apids = sorted(set(data["CCSDS_APID"].tolist()))
    log.info(f"Parsed APID(s): {unique_apids}")

    # drop the primary header fields, callers only expect the hk fields
    for header_field in (
        "CCSDS_VERSION_NUMBER",
        "CCSDS_PACKET_TYPE",
        "CCSDS_SECONDARY_FLAG",
        "CCSDS_SEQUENCE_FLAG",
        "CCSDS_APID",
        "CCSDS_SEQUENCE_COUNT",
        "CCSDS_PACKET_LENGTH",
    ):
        data.pop(header_field, None)

    return data


# CATDESC text for each field in hermes_EEA_hk_packet_def.csv (excluding SHCOARSE/SHFINE,
# which are consumed to derive the Epoch rather than stored as their own measurement).
HK_FIELD_CATDESC = {
    "SHFILL": "CCSDS Packet 2nd Header Fill",
    "SHEID": "CCSDS Packet 2nd Header Extended ID",
    "FILL": "Fill",
    "UPLOAD_STATE": "Upload Data sub-state",
    "EEA_OPMODE": "EEA operating mode",
    "FAILFC": "EEA failed TC function code",
    "FILL2": "Fill",
    "SAFESRC": "EEA safe mode source",
    "FILL3": "Fill",
    "TCBUFSEU": "EEA TC buffer SEU",
    "TCTMRERR": "EEA TC buffer TMR error",
    "TMBUFSEU": "EEA TM fifo SEU",
    "TMTMRERR": "EEA TM fifo TMR error",
    "TMUFIOW": "EEA TM fifo underflow error",
    "T_FEE": "EEA Front End Electronics Board temp",
    "FILL4": "Fill",
    "V_5_7I": "EEA 5.7V current monitor",
    "V_5_7V": "EEA 5.7V voltage monitor",
    "V_NS_7V": "EEA -5.7V voltage monitor",
    "V_11": "EEA 11V current monitor",
    "V_11V": "EEA 11V voltage monitor",
    "V_3_3V": "EEA 3.3V Voltage monitor",
    "V_3_3I": "EEA 3.3V current monitor",
    "T_LVPS": "EEA LVPS temperature",
    "ANODE_V": "Anode_mon",
    "ESA_BULK_V": "ESA_Bulk_mon",
    "DEF_BULK_V": "Deflector_Bulk_mon",
    "FILL5": "Fill",
    "V_IO_PLUG": "V/10 Plug State",
    "STPR_TBL": "Stepper Table Selection",
    "STPR_EN": "Stepper Enable bit",
    "PPS_DUR": "Duration since last PPS",
    "TIME_DUR": "Duration since last Time Packet",
    "CKSUM16": "Checksum",
}


def l0_hk_data_to_cdf(data: dict, original_filename: Path, destination_dir: Path) -> Path:
    """
    Write level 0 eea housekeeping data to a level 1 cdf file.

    Parameters
    ----------
    data: dict
        A dictionary of arrays which includes the housekeeping fields
        (as returned by parse_hk_packets), including SHCOARSE/SHFINE.
    original_filename: Path
        The Path to the originating file.
    destination_dir: Path
        The directory to write the output cdf file to.

    Returns
    -------
    output_filename: Path
        Fully specificied filename of cdf file
    """
    file_metadata = parse_science_filename(original_filename.name)

    cdf_filename = destination_dir / create_science_filename(
        file_metadata["instrument"],
        file_metadata["time"],
        "l1",
        f'1.0.{file_metadata["version"]}',
    )

    epoch = ccsds_to_cdf_time.help_convert_eaa(data)
    iso_datetimes = Time([lib.tt2000_to_datetime(e) for e in epoch])
    hk_timeseries = TimeSeries(time=iso_datetimes)

    bare_attrs = HermesData.global_attribute_template("eea", "l1", "1.0.0")
    hermes_eea_hk_data = HermesData(timeseries=hk_timeseries, meta=bare_attrs)

    # SHCOARSE/SHFINE were only needed to derive the epoch above, everything else
    # is stored as raw, dimensionless counts for now since calibration curves for
    # voltages/temperatures are not yet defined (same approach as the science data).
    for field, values in data.items():
        if field in ("SHCOARSE", "SHFINE"):
            continue
        try:
            hermes_eea_hk_data.add_measurement(
                f"hermes_eea_{field.lower()}",
                astropy_units.Quantity(values, astropy_units.dimensionless_unscaled),
                meta={"CATDESC": HK_FIELD_CATDESC.get(field, f"HK field {field}")},
            )
        except Exception as e:
            log.warning(f"Could not add HK field {field}: {e}")

    try:
        cdf_path = hermes_eea_hk_data.save(destination_dir, True)
    except Exception as e:
        log.error(e)
        sys.exit(2)

    return cdf_path


def l0_sci_data_to_cdf(stepper, data: dict, original_filename: Path, destination_dir: Path
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

    cdf_filename = original_filename.parent / create_science_filename(
        file_metadata["instrument"],
        file_metadata["time"],
        "l1",
        f'1.0.{file_metadata["version"]}',
    )
    if data:
        """
        hermes_eea.stepper_table for now is defined in hermes_eea/hermes_eea/__init__.py
        """
      
        # calibration_file = get_calibration_file(hermes_eea.stepper_table)
        # read_calibration_file(calibration_file)

        myEEA = EEA(file_metadata)
        # SkymapFactory, now as does FPI, also populates my EEA data model
        skymap_factory(data, stepper, myEEA)

        # In the beginning, testing phase of this project, while we adjust things.
        # This will show us which packets have a workable amount of data
        # most_active = np.where(np.array(myEEA.stats) > 150)
        # these eample start times are also something I would like to keep around for a while
        # example_start_times = Time(
        #    [lib.tt2000_to_datetime(e) for e in myEEA.Epoch[0:10]]
        # )

        n_packets = len(myEEA.Epoch)

        # https://hermes-core.readthedocs.io/en/latest/user-guide/reading_writing_data.html
        # https://hermes-core.readthedocs.io/en/latest/generated/api/hermes_core.timedata.HermesData.html#hermes_core.timedata.HermesData
        hermes_eea_factory = Hermes_EEA_Data_Processor(myEEA)
        hermes_eea_factory.build_HermesData()

        try:
            # this writes out the data to CDF file format
            cdf_path = hermes_eea_factory.hermes_eea_data.save(
                destination_dir, True
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
    return os.path.join(hermes_eea.getCalibrationDirectory(), data_filename)


def read_calibration_file(calib_filename: Path):
    """
    Given a calibration, return the calibration structure.

    Parameters
    ----------
    DJG says that energies and angles may change
    calib_filename: str
        Fully specificied filename of the non-calibrated file (data level < 2)
        0 1
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
