import os

from hermes_eea.Stepper.StepperTable import StepperTable

STEPPER_TABLE_FOR_FILE = {

    
    "hermes_EEA_l0_2026161-132236_v0.bin": {
        "apid": 260,
        "stepper_table": "ptb_esastepped_undeflected_stepper.txt",
    },
    
    "hermes_EEA_hk_l0_2026161-132237_v0.bin": {"apid": 265, "stepper_table": None},
    "hermes_EEA_hk_l0_2026023-000000_v0.bin": {"apid": 265, "stepper_table": None},
    "hermes_EEA_l0_2026023-000000_v0.bin": {
        "apid": 260,
        "stepper_table": "ptb_esastepped_undeflected_stepper.txt",
    },
    "hermes_EEA_l0_2023042-000000_v0.bin": {
        "apid": 260, 
        "stepper_table": "flight_stepper.txt"},
}

# Which APID and stepper table file applies to which test L0 input file.
single_stepper_table_for_file = {
     "hermes_EEA_l0_2023042-000000_v0.bin": {
        "apid": 260, 
        "stepper_table": "flight_stepper.txt"},
}


def get_stepper_table_for_file(data_filename) -> "StepperTable":
    """Look up and build the StepperTable that applies to a given test L0 input file.

    Parameters
    ----------
    data_filename: str or Path
        The L0 input filename (only the basename is used for the lookup).

    Raises
    ------
    KeyError
        If no stepper table is registered for this filename.
    """
    name = os.path.basename(str(data_filename))
    try:
        stepper_table_name = STEPPER_TABLE_FOR_FILE[name]["stepper_table"]
    except KeyError:
        raise KeyError(
            f"No stepper table is registered for input file {name!r}. "
            f"Known files: {sorted(STEPPER_TABLE_FOR_FILE)}"
        )
    if stepper_table_name is None:
        return None
    return StepperTable(stepper_table_name)


def get_apid_for_file(data_filename) -> int:
    """Look up the CCSDS APID that applies to a given test L0 input file."""
    name = os.path.basename(str(data_filename))
    try:
        return STEPPER_TABLE_FOR_FILE[name]["apid"]
    except KeyError:
        raise KeyError(
            f"No APID is registered for input file {name!r}. "
            f"Known files: {sorted(STEPPER_TABLE_FOR_FILE)}"
        )
