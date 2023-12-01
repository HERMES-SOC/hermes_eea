# Licensed under Apache License v2 - see LICENSE.rst
import os.path
import sys
sys.path.append(os.getcwd())
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


log.info(f"hermes_eea version: {__version__}")

skeleton = str( os.path.join(_data_directory, "masterSkeletons", "hermes_eea_l0_00000000000000_v0.0.0.cdf") )
stepper_table = "flight_stepper.txt"


energies = [2.18000000e+00, 2.63177330e+00, 3.17717004e+00, 3.83559233e+00,
       4.63046306e+00, 5.59005918e+00, 6.74851766e+00, 8.14704980e+00,
       9.83540739e+00, 1.18736525e+01, 1.43342944e+01, 1.73048684e+01,
       2.08910507e+01, 2.52204172e+01, 3.04469818e+01, 3.67566761e+01,
       4.43739626e+01, 5.35698211e+01, 6.46713874e+01, 7.80735920e+01,
       9.42532085e+01, 1.13785815e+02, 1.37366271e+02, 1.65833433e+02,
       2.00200000e+02, 2.39800000e+02, 3.17794829e+02, 4.21157437e+02,
       5.58138682e+02, 7.39673007e+02, 9.80251281e+02, 1.29907752e+03,
       1.72160182e+03, 2.28155195e+03, 3.02362557e+03, 4.00705827e+03,
       5.31035195e+03, 7.03754125e+03, 9.32649800e+03, 1.23599368e+04,
       1.63800000e+04]
