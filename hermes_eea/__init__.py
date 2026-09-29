# Licensed under Apache License v2 - see LICENSE.rst
from pathlib import Path

from hermes_core import log
from hermes_eea.io.file_tools import read_file

try:
    from ._version import __version__
    from ._version import version_tuple
except ImportError:
    __version__ = "unknown"
    version_tuple = (0, 0, "unknown version")

__all__ = ["log", "read_file"]

INST_NAME = "eea"
INST_SHORTNAME = "eea"
INST_TARGETNAME = "EEA"
INST_TO_SHORTNAME = {INST_NAME: INST_SHORTNAME}
INST_TO_TARGETNAME = {INST_NAME: INST_TARGETNAME}

_package_directory = Path(__file__).parent
_data_directory = _package_directory / "data"
_calibration_directory = _data_directory / "calibration"


log.info(f"hermes_eea version: {__version__}")

FirstStepperTable = "flight_stepper.txt"


def getCalibrationDirectory():
    return _calibration_directory
