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
from hermes_core import log
import numpy as np


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
            verify_l1a(output_files[0])

    # Ensure the temporary directory is cleaned up even if an exception is raised (needed for Windows)
    except PermissionError:
        print("Encountered a PermissionError, retrying file deletion...")
        time.sleep(0.5)  # Wait a bit for the OS to release any locks
        cleanup_retry(tmpdirname)


def verify_l1a(output_l1a):
    """
    We haven't decided yet on variables really
    """
    assert os.path.getsize(output_l1a) > 275000
    with pycdf.CDF(output_l1a) as cdf:

        # overall structure
        length_vars = len(cdf["Epoch"][:])
        length_time = (cdf["Epoch"][-1] - cdf["Epoch"][0]).total_seconds()
        nSteps = len(calib.energies)
        assert len(cdf["Epoch"][:]) == 18
        log.info("Length of CDF Variables: %d" % length_vars)
        log.info("Time   of CDF Variables: %d" % length_time)

        assert abs(length_time - length_vars) < 2  # each sweep is about 1 sec

        # review variables
        variable_list = [item[0] for item in list(cdf.items())]
        for var in variable_list:
            log.info(var)
            ndims = len(cdf[var].shape)

        # look at the counts 
            # best guess at counter variable
            if "count" in var:
                counter = var
            if "accum" in var:
                skymap = var

            assert cdf[var].shape[0] == length_vars
            if len(cdf[var].shape) >= 2 and "INT" in str(cdf[var]):
                assert cdf[var].shape[1] == nSteps
        for i in range(0, length_vars):
            total = np.sum(cdf[skymap][i])
            cntsum = np.sum(cdf[counter][i])

            # 40% seems like a lot... This is because this is not just for one packet but a whole sweep 
            # that's why I created my STATS variable.
            # 1 is nominal but 40% is possible for small counts
            diff = int(0.4 * total)

            log.info("totals: skymap:%d counter:%d" % (total, cntsum))
            assert abs(cntsum - total) <= diff

    shutil.copy(output_l1a, "/workspaces/hermes_eea/hermes_eea/data")


def cleanup_retry(directory):
    """Attempt to clean up the directory after a short delay."""
    try:
        shutil.rmtree(directory)
    except PermissionError as e:
        print(f"Failed to clean up directory {directory} due to PermissionError: {e}")
