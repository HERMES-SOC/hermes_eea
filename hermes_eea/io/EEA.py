
class EEA:
    def __init__(self, conf):
        self.Epoch = [] # the first of each sweep, the first of each of the 164 times,
        #                 when hermes_eea_intgr_or_stepper = 1 and  hermes_eea_step_counter = 0
        self.Generation_date = None
        self.Logical_file_id = None
        self.Data_version = None
                             # ener, defl
        self.µEpoch = []     #[ 41,  4 ] each of the 164 times, whenever hermes_eea_intgr_or_stepper == 1
        self.PulseA  = []    # [41, 4] overflow[0],accum[33]
        self.PulseB  = []    # [41, 4] overflow[1], accum[34]
        self.Counter1 = []
        self.Counter2 = []
        self.ACCUM   = []    # [41, 4, 32]. [ene, defl, accums]
        self.SunAngles = [] # [4,32] really just metadata
        self.EnergyLabels = []# [41] really just metadata
        self.stats = []# [41] really just metadata


    def append(self, attrname, record):
        try:
            return record[attrname]
        except KeyError:
            # occasionally no value is returned see: compressionLoss is only in moms brst
            if self.name_align(attrname) in self.default_obj:
                return self.default_obj[self.name_align(attrname)]

    def populate(self, myEEA, skymap):

        packet = 0
        for record in skymap:
            myEEA.µEpoch.append(record['µEpoch'])
            myEEA.Epoch.append(record['Epoch'])
            myEEA.ACCUM.append(record['counts'])
            myEEA.PulseA.append(record['pulse_a'])
            myEEA.PulseB.append(record['pulse_b'])
            myEEA.SunAngles.append(record['sun_angles'])
            myEEA.EnergyLabels.append(record['energies'])
            myEEA.Counter1.append(record['counter1'])
            myEEA.Counter2.append(record['counter2'])
            myEEA.stats.append(record['stats'])


