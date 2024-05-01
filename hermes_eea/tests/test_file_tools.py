import os
import hermes_eea
from hermes_eea.io.file_tools import read_file
from hermes_eea.Stepper.Stepper_Table import Stepper_Table
from pathlib import Path
import pytest


def test_read_file():
    assert read_file("./hermes_eea/data/calibration/flight_stepper.txt") is not None


@pytest.fixture(scope="session")  # this is a pytest fixture
def first_stepper_file(tmp_path_factory):
    fn = Path(os.path.join(hermes_eea.stepper_table))
    return fn

def test_characterize_stepper(first_stepper_file):
     stepper = Stepper_Table(first_stepper_file)
     assert len(stepper.energies) == 164