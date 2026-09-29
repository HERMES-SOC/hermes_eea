import pytest
from pathlib import Path
import shutil
import tempfile
import time
import ccsdspy
import hermes_eea
from hermes_eea.calibration.calibration import _peek_apid
from hermes_eea.io import read_ccsds
import hermes_eea.calibration as calib
from hermes_eea import _data_directory, FirstStepperTable 
from hermes_core.util.util import create_science_filename, parse_science_filename
import sys
from spacepy import pycdf
from hermes_core import log
import numpy as np
from hermes_eea.Stepper.StepperTable import StepperTable
from hermes_eea.tests.conftest import STEPPER_TABLE_FOR_FILE, get_stepper_table_for_file, get_apid_for_file

@pytest.fixture( scope="session", params=list(STEPPER_TABLE_FOR_FILE), ids=lambda bin_name: bin_name,)  # this is a pytest fixture
def small_level0_file(request):
    return Path(os.path.join(_data_directory, request.param))


def test_read_ccsdspy(small_level0_file):
    """
    Homage to Liam and the difficulties encountered at the outset...
    Parameters
    ----------
    small_level0_file - ccsds format packet file

    Returns
    -------

    """
    apid = get_apid_for_file(small_level0_file)
    # HK and science packets use different fixed-length layouts.
    is_hk = apid == 265
    packet_def_csv = "hermes_EEA_hk_packet_def.csv" if is_hk else "hermes_EEA_sci_packet_def.csv"
    pkt = ccsdspy.FixedLength.from_file(
        os.path.join(hermes_eea._data_directory, packet_def_csv)
    )
    result = read_ccsds(small_level0_file, pkt)
    if is_hk:
        assert len(result["SHCOARSE"]) > 0
    else:
        assert len(result["ACCUM"]) > 0


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
<<<<<<< HEAD
            verify_l1a(small_level0_file, output_files[0])
            # HK verification, once it exists. Copy out for inspection in the meantime.
            shutil.copy(output_files[0], "/workspaces/hermes_eea/hermes_eea/data")
=======

            for f in output_files:
                assert isinstance(f, Path)
            assert output_files[0].stat().st_size > 0

            # Ensure the file is closed before attempting to delete it
            with pycdf.CDF(str(output_files[0])) as cdf:
                assert len(cdf["Epoch"][:]) == 18
>>>>>>> main

    # Ensure the temporary directory is cleaned up even if an exception is raised (needed for Windows)
    except PermissionError:
        print("Encountered a PermissionError, retrying file deletion...")
        time.sleep(0.5)  # Wait a bit for the OS to release any locks
        cleanup_retry(tmpdirname)


def verify_l1a(data_filename, output_l1a):
    """
    We haven't decided yet on variables really
    """
    # Determine the APID (and, for science data, the StepperTable) from the file itself.
    apid = _peek_apid(data_filename)
    # So far there is only one StepperTable in use for science data.
    stepper = StepperTable(hermes_eea.FirstStepperTable) if apid == 260 else None
    
    from hermes_eea.io.EEA import REAL4FILL, EPOCHTIMEFILL, INTFILL
    assert os.path.getsize(output_l1a) > 275000
    with pycdf.CDF(str(output_l1a)) as cdf:

        # overall structure
        n_sweeps = len(cdf["Epoch"][:])
        length_time = (cdf["Epoch"][-1] - cdf["Epoch"][0]).total_seconds()

        assert n_sweeps > 0
        log.info("Length of CDF Variables: %d" % n_sweeps)
        log.info("Time   of CDF Variables: %d" % length_time)

        avg_sweep_seconds = length_time / max(n_sweeps - 1, 1)
        log.info("Average time per sweep: %.3f sec" % avg_sweep_seconds)
        assert avg_sweep_seconds > 0  # time should move forward, sweep to sweep

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

            assert cdf[var].shape[0] == n_sweeps
            if len(cdf[var].shape) >= 2 and "INT" in str(cdf[var]):
                print(var)
                assert cdf[var][0][stepper.n_defl * stepper.n_energies] in [REAL4FILL, EPOCHTIMEFILL, INTFILL]
        
        try:
          for i in range(0, n_sweeps):
            skymap_vals = cdf[skymap][i]
            counter_vals = cdf[counter][i]
            total = np.sum(skymap_vals[skymap_vals != REAL4FILL])
            cntsum = np.sum(counter_vals[counter_vals != INTFILL])

            # 40% seems like a lot... This is because this is not just for one packet but a whole sweep 
            # that's why I created my STATS variable.
            # is nominal but 40% is possible for small counts
            diff = int(0.4 * total)

            # log.info("totals: skymap:%d counter:%d" % (total, cntsum))
            # assert abs(cntsum - total) <= diff
        except NameError as e:
            log.error(f"Error verifying L1A file {output_l1a}: {e} skymap not defined")

    shutil.copy(output_l1a, "/workspaces/hermes_eea/hermes_eea/data")


def cleanup_retry(directory):
    """Attempt to clean up the directory after a short delay."""
    try:
        shutil.rmtree(directory)
    except PermissionError as e:
        print(f"Failed to clean up directory {directory} due to PermissionError: {e}")
