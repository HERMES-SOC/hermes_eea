
from hermes_core.timedata import HermesData
import astropy.units as astropy_units
from astropy.timeseries import TimeSeries
from astropy.time import Time
from hermes_core.timedata import HermesData
from astropy.nddata import NDData
from ndcube import NDCube, NDCollection
from hermes_eea.util.time.iso_epoch import epoch_to_iso_obj, epoch_to_eea_iso, epoch_to_iso
import numpy as np
from astropy.wcs import WCS

class Build_Hermes_EEA_Data:

    def __init__(self, myEEA):
        self.EEA = myEEA
        self.raw_counts = astropy_units.def_unit("raw instrument counts")
    def build_HermesData(self):
        iso_times = Time(epoch_to_iso(self.EEA.Epoch[:]), scale='utc')
        ts_1d_uQ = TimeSeries(
            time=iso_times,
            data={"hermes_eea_stats": astropy_units.Quantity(self.EEA.stats, "gauss", dtype=np.uint16)}
        )  # this works
        self._hermes_eea_spectra()
        bare_attrs = HermesData.global_attribute_template("eea", "l1", "1.0.0")
        ts_justTime = TimeSeries(time=iso_times)

        self.hermes_eea_data = HermesData(timeseries=ts_1d_uQ, spectra=self.multiple_spectra, meta=bare_attrs)
        self.hermes_eea_data.timeseries['hermes_eea_stats'].meta.update({"CATDESC": "Sum of skymap for each sweep"})

    def _hermes_eea_spectra(self):
        self.multiple_spectra = NDCollection(
            [
                ("hermes_eea_settle_step_times",
                 NDCube(data=np.array(self.EEA.µEpoch), wcs=WCS(naxis=2), meta={"CATDESC": "Settle for Each Step"},
                        unit="s", )),
                ("hermes_eea_energy_profile",
                 NDCube(data=np.array(self.EEA.EnergyLabels), wcs=WCS(naxis=2), meta={"CATDESC": "Energy Profile"},
                        unit="eV", )),
                ("hermes_eea_accum",
                 NDCube(data=np.array(self.EEA.ACCUM), wcs=WCS(naxis=3), meta={"CATDESC": "EEA raw skymap"},
                        unit="count" )),

                ("hermes_eea_counter1",
                 NDCube(data=np.array(self.EEA.Counter1), wcs=WCS(naxis=2),
                        meta={"CATDESC": "Estimate 1 of the number of counts in this accumulation"},
                        unit=astropy_units.dimensionless_unscaled, )),

                ("hermes_eea_counter1",
                 NDCube(data=np.array(self.EEA.Counter1), wcs=WCS(naxis=2),
                        meta={"CATDESC": "Estimate 1 of the number of counts in this accumulation"},
                        unit=astropy_units.dimensionless_unscaled, )),
                ("hermes_eea_counter2",
                 NDCube(data=np.array(self.EEA.Counter1), wcs=WCS(naxis=2),
                        meta={"CATDESC": "Estimate 1 of the number of counts in this accumulation"},
                        unit=astropy_units.dimensionless_unscaled, ))
            ])