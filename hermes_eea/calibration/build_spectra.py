from hermes_core.timedata import HermesData
import astropy.units as astropy_units
from astropy.timeseries import TimeSeries
from astropy.time import Time
from hermes_core.timedata import HermesData
from astropy.nddata import NDData
from ndcube import NDCube, NDCollection
import numpy as np
from astropy.wcs import WCS
from spacepy.pycdf import lib
import csv
import os
import hermes_eea


def _read_sci_field_catdesc() -> dict:
    """Read the CATDESC text for each field from the description column of
    hermes_EEA_sci_packet_def.csv, so descriptions stay in sync with the packet
    definition instead of being duplicated in code.
    """
    csv_path = os.path.join(hermes_eea._data_directory, "hermes_EEA_sci_packet_def.csv")
    with open(csv_path, "r") as fp:
        reader = csv.DictReader(fp, skipinitialspace=True)
        return {row["name"].strip(): row["description"].strip() for row in reader}


# CATDESC text for spectra variables that are derived (via SkymapFactory/StepperTable)
# rather than decoded directly from a packet field, so they have no row in
# hermes_EEA_sci_packet_def.csv or the stepper table files.
DERIVED_SPECTRA_CATDESC = {
    "hermes_eea_step_times": "Raw Per-Step Packet Time",
    "hermes_eea_energy_profile": "Energy Profile",
    "hermes_eea_deflection_angles": "Deflection Angles",
    "hermes_eea_pulse_a": "TOF Channel A Overflow Counter (raw ACCUM bin 33)",
    "hermes_eea_pulse_b": "TOF Channel B Overflow Counter (raw ACCUM bin 32)",
}


class Hermes_EEA_Data_Processor:
    """
    This class plays the role of that the Write* classes provided in the pyFPI GroundSystm (HIGS)
    It not only handles the populating and writing of the cdf but attibutes are also added here.
    """

    def __init__(self, myEEA):
        self.EEA = myEEA
        # Dan Gershman has yet to provide direction on the details of the EEA variable descriptions
        # As such we have temporarily added convenience variables such as Stats - which provides
        # a sum of the counts in each packet.

        # I'm leaving this here for future pre-flight reference
        self.raw_counts = astropy_units.def_unit("raw instrument counts")

    def build_HermesData(self):
        """
        time - an EEA Single dimension variable
        # this function sets/prepares the variables for writing. Here is
        # an example of handling a variable in the traditional non-NDCube way.
        """
        # cdf:
        # iso_str_times = Time(epoch_to_iso(self.EEA.Epoch[:]), scale='utc')
        # cdflib -> astropy
        iso_datetimes = Time([lib.tt2000_to_datetime(e) for e in self.EEA.Epoch[:]])
        quantity_time = self.EEA.Epoch[:] * astropy_units.second

        #
        ts_1d_uQ = TimeSeries(time=iso_datetimes)

        self._hermes_eea_spectra()
        bare_attrs = HermesData.global_attribute_template("eea", "l1", "1.0.0")
        ts_justTime = TimeSeries(time=iso_datetimes)

        self.hermes_eea_data = HermesData(
            timeseries=ts_1d_uQ,  # this is stats time series ....with no stats...
            spectra=self.multiple_spectra,
            meta=bare_attrs,
        )
        # self.hermes_eea_data.timeseries["hermes_eea_stats"].meta.update(
        #    {"CATDESC": "Sum of skymap particle count for each sweep"}
        # )

    def _hermes_eea_spectra(self):
        """
        EEA multi-dimensional variables
        This is a solution for loading multi-dimension variables and their metadata into CDF
        HermesData is used for "regular" time-series variables such as the Epoch and stats variables above.
        """
        catdesc = _read_sci_field_catdesc()

        self.multiple_spectra = NDCollection(
            [
                (
                    "hermes_eea_step_times",
                    NDCube(
                        data=np.array(self.EEA.usec),
                        wcs=WCS(naxis=2),
                        meta={"CATDESC": DERIVED_SPECTRA_CATDESC["hermes_eea_step_times"]},
                        unit=astropy_units.s,
                    ),
                ),
                (
                    "hermes_eea_energy_profile",
                    NDCube(
                        data=np.array(self.EEA.EnergyLabels),
                        wcs=WCS(naxis=2),
                        meta={"CATDESC": DERIVED_SPECTRA_CATDESC["hermes_eea_energy_profile"]},
                        unit=astropy_units.eV,
                    ),
                ),
                (
                    "hermes_eea_deflection_angles",
                    NDCube(
                        data=np.array(self.EEA.SunAngles),
                        wcs=WCS(naxis=2),
                        meta={"CATDESC": DERIVED_SPECTRA_CATDESC["hermes_eea_deflection_angles"]},
                        unit=astropy_units.deg,
                    ),
                ),
                (
                    "hermes_eea_accum",
                    NDCube(
                        data=np.array(self.EEA.ACCUM),
                        wcs=WCS(naxis=3),
                        meta={"CATDESC": catdesc["ACCUM"]},
                        unit=astropy_units.dimensionless_unscaled,
                    ),
                ),
                (
                    "hermes_eea_counter1",
                    NDCube(
                        data=np.array(self.EEA.Counter1),
                        wcs=WCS(naxis=2),
                        meta={"CATDESC": catdesc["COUNTER1"]},
                        unit=astropy_units.dimensionless_unscaled,
                    ),
                ),
                (
                    "hermes_eea_counter2",
                    NDCube(
                        data=np.array(self.EEA.Counter2),
                        wcs=WCS(naxis=2),
                        meta={"CATDESC": catdesc["COUNTER2"]},
                        unit=astropy_units.dimensionless_unscaled,
                    ),
                ),
                (
                    "hermes_eea_pulse_a",
                    NDCube(
                        data=np.array(self.EEA.PulseA),
                        wcs=WCS(naxis=2),
                        meta={"CATDESC": DERIVED_SPECTRA_CATDESC["hermes_eea_pulse_a"]},
                        unit=astropy_units.dimensionless_unscaled,
                    ),
                ),
                (
                    "hermes_eea_pulse_b",
                    NDCube(
                        data=np.array(self.EEA.PulseB),
                        wcs=WCS(naxis=2),
                        meta={"CATDESC": DERIVED_SPECTRA_CATDESC["hermes_eea_pulse_b"]},
                        unit=astropy_units.dimensionless_unscaled,
                    ),
                ),
            ]
        )
