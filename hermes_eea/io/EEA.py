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
        self.PulseA = []  # [41, 4] overflow[0],accum[33]
        self.PulseB = []  # [41, 4] overflow[1], accum[34]
        self.Counter1 = []
        self.Counter2 = []
        self.ACCUM = []  # [41, 4, 32]. [ene, defl, accums]
        self.SunAngles = []  # [4,32] really just metadata
        self.EnergyLabels = []  # [41] really just metadata
        self.stats = []  # [41] really just metadata

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
            self.SunAngles.append(self.append("sun_angles", record))
            self.EnergyLabels.append(self.append("energies", record))
            self.Counter1.append(record["counter1"])
            self.Counter2.append(record["counter2"])
            self.stats.append(record["stats"])
