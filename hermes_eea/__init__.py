# Licensed under Apache License v2 - see LICENSE.rst
import os.path
import sys

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

_package_directory = os.path.dirname(os.path.abspath(__file__))
_data_directory = os.path.abspath(os.path.join(_package_directory, "data"))
_calibration_directory = os.path.abspath(os.path.join(_data_directory, "calibration"))


log.info(f"hermes_eea version: {__version__}")

stepper_table = "flight_stepper.txt"
