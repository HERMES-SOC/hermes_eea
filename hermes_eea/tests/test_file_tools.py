import pytest
import os.path
from pathlib import Path

import hermes_eea
from hermes_eea.io import load_data_file, read_calibration_file, write_data_file

level0_filename = "hermes_EEA_l0_2022339-000000_v0.bin"
level1_filename = "hermes_eea_l1_20221205T000000_v1.0.0.cdf"
ql_filename = "hermes_eea_ql_20221205T000000_v1.0.0.cdf"


@pytest.fixture(scope="session")
def level0_file(tmp_path_factory):
    fn = tmp_path_factory.mktemp("data") / level0_filename
    with open(fn, "w"):
        pass
    return fn


@pytest.fixture(scope="session")
def level1_file(tmp_path_factory):
    fn = tmp_path_factory.mktemp("data") / level1_filename
    with open(fn, "w"):
        pass
    return fn


def test_load_data_file(level0_file):
    with pytest.raises(FileNotFoundError) as excinfo:
        _ = load_data_file(level0_file)
    csv_path = os.path.join(hermes_eea._data_directory, "EEA_sci_packet_def.csv")
    assert str(excinfo.value) == f"[Errno 2] No such file or directory: '{csv_path}'"


def test_read_calibration_file():
    assert read_calibration_file("calib_file") is None
