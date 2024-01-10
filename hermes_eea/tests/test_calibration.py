import pytest
import os.path
from pathlib import Path
import tempfile
import ccsdspy
import hermes_eea.calibration as calib
from hermes_eea import _data_directory, stepper_table
from hermes_core.util.util import create_science_filename, parse_science_filename
import sys


@pytest.fixture(scope="session")  # this is a pytest fixture
def small_level0_file(tmp_path_factory):
    fn = Path(os.path.join(_data_directory, "hermes_EEA_l0_2023042-000000_v0.bin"))
    return fn


def test_calibrate_file(small_level0_file):
    """Test that the output filenames are correct and that a file was actually created."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        output_file = calib.calibrate_file(small_level0_file, Path(tmpdirname))
        assert (
            os.path.basename(output_file) == "hermes_eea_l1_20000101T170901_v1.0.0.cdf"
        )
        assert os.path.getsize(output_file) > 200000
