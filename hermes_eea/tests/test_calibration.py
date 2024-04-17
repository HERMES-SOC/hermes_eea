import pytest
import os.path
from pathlib import Path
import shutil
import tempfile
import time
import ccsdspy
import hermes_eea
from hermes_eea.io import read_ccsds
import hermes_eea.calibration as calib
from hermes_eea import _data_directory, stepper_table
from hermes_core.util.util import create_science_filename, parse_science_filename
import sys
from spacepy import pycdf


@pytest.fixture(scope="session")  # this is a pytest fixture
def small_level0_file(tmp_path_factory):
    fn = Path(os.path.join(_data_directory, "hermes_EEA_l0_2023042-000000_v0.bin"))
    return fn


def test_read_ccsdspy(small_level0_file):
    """
    Homage to Liam and the difficulties encountered at the outset...
    Parameters
    ----------
    small_level0_file - ccsds format packet file

    Returns
    -------

    """
    pkt = ccsdspy.FixedLength.from_file(
        os.path.join(hermes_eea._data_directory, "hermes_EEA_sci_packet_def.csv")
    )
    result = read_ccsds(small_level0_file, pkt)
    assert len(result["ACCUM"]) == 3051


def test_process_file(small_level0_file):
    """Test the boilerplate of the file processing function
       Tests a creation of a nominal L1A EEA file from packets
    calls:
        CCSDSPY
        A Custom EEA SkymapFactory
        HermesData
    """
    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Create a Temp Copy of the Original
            temp_test_file_path = Path(tmpdirname, small_level0_file.name)
            shutil.copy(small_level0_file, temp_test_file_path)
            # Process the File
            output_files = calib.process_file(temp_test_file_path)
            shutil.copy(output_files[0], '/workspaces/hermes_eea/hermes_eea/data')
            assert os.path.getsize(output_files[0]) > 275000

            # Ensure the file is closed before attempting to delete it
            with pycdf.CDF(output_files[0]) as cdf:
                assert len(cdf["Epoch"][:]) == 18

    # Ensure the temporary directory is cleaned up even if an exception is raised (needed for Windows)
    except PermissionError:
        print("Encountered a PermissionError, retrying file deletion...")
        time.sleep(0.5)  # Wait a bit for the OS to release any locks
        cleanup_retry(tmpdirname)


def cleanup_retry(directory):
    """Attempt to clean up the directory after a short delay."""
    try:
        shutil.rmtree(directory)
    except PermissionError as e:
        print(f"Failed to clean up directory {directory} due to PermissionError: {e}")
