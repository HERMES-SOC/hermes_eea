N_AZIMUTH = 32  # number of real sky-map azimuth bins
# The raw ACCUM packet field has 34 channels total (see hermes_EEA_sci_packet_def.csv).
# Confirmed against the EEA C&DH firmware (GitLab hermes-eea/eea-cdh, eea.vhd/eea_ctrl.vhd):
# channels 0-31 are the real sky-map azimuth bins; the last two are TOF-ASIC overflow
# counters, not azimuth data:
#   ACCUM bin 32 (0-indexed) -> TOF channel B overflow (PulseB)
#   ACCUM bin 33 (0-indexed) -> TOF channel A overflow (PulseA)
PULSE_B_CHANNEL = N_AZIMUTH      # 32
PULSE_A_CHANNEL = N_AZIMUTH + 1  # 33
MAX_STEPS = 256
REAL4FILL = -1E+31
# this large negative number is cdfepoch of 9999-12-31T23:59:59.999999999 which is the fillvalue from...Hermes/Astropy or something
EPOCHTIMEFILL = -9223372036854775808
INTFILL = 65535

class EEA:
    """
    holds the data after Skymap creation and before CDF file population
    """
    def __init__(self, conf):
        self.Epoch = []  # the first of each sweep, the first of each of the 164 times,
        #                 when hermes_eea_intgr_or_stepper = 1 and  hermes_eea_step_counter = 0
        self.Generation_date = None
        self.Logical_file_id = None
        self.Data_version = None
        # ener, defl
        self.usec = (
            []
        )  # [ 41,  4 ] each of the 164 times, whenever hermes_eea_intgr_or_stepper == 1
        self.PulseA = []  # [n_sweeps, MAX_STEPS] TOF channel A overflow counter (ACCUM bin 33)
        self.PulseB = []  # [n_sweeps, MAX_STEPS] TOF channel B overflow counter (ACCUM bin 32)
        self.Counter1 = []
        self.Counter2 = []
        self.ACCUM = []  # [41, 4, 32]. [ene, defl, accums]
        self.SunAngles = []  # [4,32] really just metadata
        self.EnergyLabels = []  # [41] really just metadata
        # self.stats = []  # [41] really just metadata

    def append(self, attrname, record):
        try:
            return record[attrname]
        except KeyError:
            # occasionally no value is returned
            if self.name_align(attrname) in self.default_obj:
                return self.default_obj[self.name_align(attrname)]

    def populate(self, skymap):
        for record in skymap:
            self.Epoch.append(record["Epoch"])
            self.usec.append(self.append("usec", record))
            self.ACCUM.append(self.append("counts", record))
            self.PulseA.append(self.append("pulse_a", record))
            self.PulseB.append(self.append("pulse_b", record))
            self.SunAngles.append(self.append("deflections", record))
            self.EnergyLabels.append(self.append("energies", record))
            self.Counter1.append(record["counter1"])
            self.Counter2.append(record["counter2"])
            
