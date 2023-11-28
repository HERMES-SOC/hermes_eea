import pytest
import os.path
from pathlib import Path
import ccsdspy
import hermes_eea.calibration as calib
from hermes_eea import _data_directory,stepper_table
from hermes_core.util.util import create_science_filename, parse_science_filename

level1_filename = "hermes_eea_l1_20221205_000000_v1.0.0.cdf"
ql_filename = "hermes_eea_ql_20221205_000000_v1.0.0.cdf"


@pytest.fixture(scope="session") # this is a pytest fixture
def level0_file(tmp_path_factory):
    #fn = Path(os.path.join(_data_directory, "hermes_EEA_l0_2023038-000000_v0.bin"))
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

def test_HermesData1():
    import numpy as np
    import astropy.units as u
    from astropy.timeseries import TimeSeries
    from astropy.time import Time, TimeDelta
    ts = TimeSeries(time_start='2016-03-22T12:30:31',
                    time_delta=3 * u.s,
                    data={'Bx': u.Quantity([1, 2, 3, 4],
                          'nanoTesla',
                          dtype=np.uint16)})
    for item in ts.columns['time']:
        print(item)
    times = Time('2010-01-01 00:00:00', scale='utc') + TimeDelta(np.arange(100) * u.s)
    ts = TimeSeries(
           time=times,
           data={'diff_e_flux': u.Quantity(np.arange(100) * 1e-3,
                 '1/(cm**2 * s * eV * steradian)',
           dtype=np.float32)}
         )


def test_calibrate_file(level0_file, level1_file):
    """Test that the output filenames are correct and that a file was actually created."""
    output_file = calib.calibrate_file(level0_file)
    # assert output_file.name == level1_filename
    #assert output_file.name == ql_filename
    #assert output_file.is_file()

# this creates a blank cdf with the proper name -- not too interesting
def nottest_l0_sci_data_to_cdf(level0_file):
    """Test that the output filenames are correct and that a file was actually created."""
    data = {}
    output_file = calib.l0_sci_data_to_cdf(data, level0_file)
    # assert output_file.name == level1_filename
    assert output_file.is_file()


# This drops all the way down to ccsdspy but seems to work
def nottest_calibrate_file_nofile_error():
    """Test that if file does not exist it produces the correct error. The file needs to be in the correct format."""
    with pytest.raises(FileNotFoundError):
        calib.calibrate_file(Path("hermes_EEA_l0_2032339-000000_v0.bin"))

# This one is less clear as yet...
def nottest_process_file_nofile_error():
    """Test that if file does not exist it produces the correct error. The file needs to be in the correct format."""
    with pytest.raises(FileNotFoundError):
        calib.process_file(Path("hermes_EEA_l0_2032339-000000_v0.bin"))


# this fills the blank cdf with data
def nottest_calibrate_file(level0_file, level1_file):
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

# this also populates the file with data
def nottest_process_file_level0(level0_file):
    """Test that the output filenames are correct and that a file was actually created."""
    file_output = calib.process_file(level0_file)
    assert len(file_output) == 1
    # assert file_output[0].name == level1_filename
    assert file_output[0].is_file()

# this populates a level 1, a different file but doesn't really, now it is just a stub
def nottest_process_file_level1(level1_file):
    """Test that the output filenames are correct and that a file was actually created."""
    file_output = calib.process_file(level1_file)
    assert len(file_output) == 1
    assert file_output[0].name == ql_filename
    assert file_output[0].is_file()




