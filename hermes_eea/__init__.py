# Licensed under Apache License v2 - see LICENSE.rst
import os.path
import sys

sys.path.append(os.getcwd())
from hermes_core import log

try:
    from ._version import __version__
    from ._version import version_tuple
except ImportError:
    __version__ = "unknown"
    version_tuple = (0, 0, "unknown version")

__all__ = ["log"]

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


energies = [
    2.18000000e00,
    2.63177330e00,
    3.17717004e00,
    3.83559233e00,
    4.63046306e00,
    5.59005918e00,
    6.74851766e00,
    8.14704980e00,
    9.83540739e00,
    1.18736525e01,
    1.43342944e01,
    1.73048684e01,
    2.08910507e01,
    2.52204172e01,
    3.04469818e01,
    3.67566761e01,
    4.43739626e01,
    5.35698211e01,
    6.46713874e01,
    7.80735920e01,
    9.42532085e01,
    1.13785815e02,
    1.37366271e02,
    1.65833433e02,
    2.00200000e02,
    2.39800000e02,
    3.17794829e02,
    4.21157437e02,
    5.58138682e02,
    7.39673007e02,
    9.80251281e02,
    1.29907752e03,
    1.72160182e03,
    2.28155195e03,
    3.02362557e03,
    4.00705827e03,
    5.31035195e03,
    7.03754125e03,
    9.32649800e03,
    1.23599368e04,
    1.63800000e04,
]
