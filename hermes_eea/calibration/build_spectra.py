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

        self.multiple_spectra = NDCollection(
            [
                (
                    "hermes_eea_settle_step_times",
                    NDCube(
                        data=np.array(self.EEA.usec),
                        wcs=WCS(naxis=2),
                        meta={"CATDESC": "Settle for Each Step"},
                        unit=astropy_units.s,
                    ),
                ),
                (
                    "hermes_eea_energy_profile",
                    NDCube(
                        data=np.array(self.EEA.EnergyLabels),
                        wcs=WCS(naxis=2),
                        meta={"CATDESC": "Energy Profile"},
                        unit=astropy_units.eV,
                    ),
                ),
                (
                    "hermes_eea_accum",
                    NDCube(
                        data=np.array(self.EEA.ACCUM),
                        wcs=WCS(naxis=3),
                        meta={"CATDESC": "EEA raw skymap counts"},
                        unit=astropy_units.dimensionless_unscaled,
                    ),
                ),
                (
                    "hermes_eea_counter1",
                    NDCube(
                        data=np.array(self.EEA.Counter1),
                        wcs=WCS(naxis=2),
                        meta={
                            "CATDESC": "Estimate 1 of the number of counts in this accumulation"
                        },
                        unit=astropy_units.dimensionless_unscaled,
                    ),
                ),
                (
                    "hermes_eea_counter1",
                    NDCube(
                        data=np.array(self.EEA.Counter1),
                        wcs=WCS(naxis=2),
                        meta={
                            "CATDESC": "Estimate 2 of the number of counts in this accumulation"
                        },
                        unit=astropy_units.dimensionless_unscaled,
                    ),
                ),
                (
                    "hermes_eea_counter2",
                    NDCube(
                        data=np.array(self.EEA.Counter1),
                        wcs=WCS(naxis=2),
                        meta={
                            "CATDESC": "Estimate 3 of the number of counts in this accumulation"
                        },
                        unit=astropy_units.dimensionless_unscaled,
                    ),
                ),
            ]
        )
