from pathlib import Path
from hermes_eea.io.file_tools import read_file


def test_read_file():
    assert (
        read_file(Path("./hermes_eea/data/calibration/flight_stepper.txt")) is not None
    )
