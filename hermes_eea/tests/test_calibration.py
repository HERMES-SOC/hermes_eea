import pytest
import os.path
from pathlib import Path
import shutil
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


def test_process_file(small_level0_file):
    """Test the boilerplate of the file processing function
       Tests a creation of a nominal L1A EEA file from packets
    calls:
        CCSDSPY
        A Custom EEA SkymapFactory
        HermesData
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create a Temp Copy of the Original
        temp_test_file_path = Path(tmpdirname, small_level0_file.name)
        shutil.copy(small_level0_file, temp_test_file_path)
        # Process the File
        output_files = calib.process_file(temp_test_file_path)
        print(output_files)


