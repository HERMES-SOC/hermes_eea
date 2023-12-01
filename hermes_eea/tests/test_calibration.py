import pytest
import os.path
from pathlib import Path
import ccsdspy
import hermes_eea.calibration as calib
from hermes_eea import _data_directory,stepper_table
from hermes_core.util.util import create_science_filename, parse_science_filename
import sys

level1a_filename = "hermes_eea_l1_20221205_000000_v1.0.0.cdf"
level1_filename  = 'hermes_eea_l1_20000101T124114_v1.0.0.cdf'
ql_filename      = "hermes_eea_ql_20221205_000000_v1.0.0.cdf"


@pytest.fixture(scope="session") # this is a pytest fixture
def small_level0_file(tmp_path_factory):
    fn = Path(os.path.join(_data_directory, "hermes_EEA_l0_2023042-000000_v0.bin"))
    return fn

@pytest.fixture(scope="session") # this is a pytest fixture
def large_level0_file(tmp_path_factory):
    fn = Path(os.path.join(_data_directory, "hermes_EEA_l0_2023041-000000_v0.bin"))
    return fn

@pytest.fixture(scope="session")
def level1_file(tmp_path_factory):
    fn = tmp_path_factory.mktemp("data") / level1_filename
    with open(fn, "w"):
        pass
    return fn

def test_get_calibration_file():
    file = Path(os.path.join(_data_directory, stepper_table))
    assert file.is_file()

def test_read_calibration_file():
    file = Path(os.path.join(_data_directory, stepper_table))
    calib.read_calibration_file(file)
    assert len(calib.energies) == 164
    assert len(calib.deflections) == 164


def test_calibrate_file(small_level0_file):
    """Test that the output filenames are correct and that a file was actually created."""
    output_file = calib.calibrate_file(small_level0_file)
    assert os.path.basename(output_file) == "hermes_eea_l1_20000101T170901_v1.0.0.cdf"
    assert os.path.getsize(output_file) > 200000

# this creates a blank cdf with the proper name -- not too interesting
def not_test_l0_sci_data_to_cdf(level0_file):
    """Test that the output filenames are correct and that a file was actually created."""
    data = {}
    output_file = calib.l0_sci_data_to_cdf(data, level0_file)
    # assert output_file.name == level1_filename
    assert output_file.is_file()


# This drops all the way down to ccsdspy but seems to work
def test_calibrate_file_nofile_error():
    """Test that if file does not exist it produces the correct error. The file needs to be in the correct format."""
    with pytest.raises(FileNotFoundError):
        calib.calibrate_file(Path("hermes_EEA_l0_2032339-000000_v0.bin"))

# This one is less clear as yet...
def test_process_file_nofile_error():
    """Test that if file does not exist it produces the correct error. The file needs to be in the correct format."""
    files = []
    files.append((Path("hermes_EEA_l0_2032339-000000_v0.bin")))
    files.append((Path("hermes_EEA_l0_2032340-000000_v0.bin")))

    with pytest.raises(FileNotFoundError):
        calib.process_file(files)


# this fills the blank cdf with data
def not_test_calibrate_file(level0_file, level1a_filename):
    """Test that the output filenames are correct and that a file was actually created."""
    output_file = calib.calibrate_file(level0_file)
    # assert output_file.name == level1_filename
    assert output_file.is_file()
    output_file = calib.calibrate_file(level1_file)
    assert output_file.name == ql_filename
    assert output_file.is_file()

    # with pytest.raises(ValueError) as excinfo:
    #    calib.calibrate_file("datafile_with_no_calib.cdf")
    # assert (
    #    str(excinfo.value)
    #    == "Calibration file for datafile_with_no_calib.cdf not found."
    # )

# this also populates the file with data..duplicate of test_calibrate_file
def test_process_file_level0(large_level0_file,small_level0_file):
    """Test that the output filenames are correct and that a file was actually created."""

    output_files = calib.process_file([large_level0_file, small_level0_file])
    assert os.path.basename(output_files[0]) == "hermes_eea_l1_20000101T124114_v1.0.0.cdf"
    assert os.path.basename(output_files[1]) == "hermes_eea_l1_20000101T170901_v1.0.0.cdf"
    assert os.path.getsize(output_files[0]) == 266568541
    assert os.path.getsize(output_files[1]) == 275299

# this populates a level 1, a different file but doesn't really, now it is just a stub
def not_test_process_file_level1(level1_file):
    """Test that the output filenames are correct and that a file was actually created."""
    file_output = calib.process_file(level1_file)
    assert len(file_output) == 1
    assert file_output[0].name == ql_filename
    assert file_output[0].is_file()




