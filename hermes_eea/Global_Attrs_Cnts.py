import os
from datetime import datetime
import math

class Global_Attrs:


    def __init__(self, version,file_id,lo_ext):

        # this is linux date format:
        self.Generation_date = datetime.now().strftime('%a %b %d %H:%M:%S %Y')
        self.Logical_file_id = os.path.basename(file_id)
        self.Data_version = version
        self.Spacecraft_attitude_filenames = ""
        self.lo_ext = lo_ext


    def setCorrectionTableValues(DES_glbattr, corrTable,conf,usec_searchfile):
        """saved in commit 2374012bbab301a23075b29c79ba9ab89285eb08
        these and others aren't needed by DES_L1A
        """
        sf_des = float(corrTable['sf_' + conf.mode])
        #DES_glbattr.Correction_table_rev                = getfilerev(corrTable["dis_p2_file_path"])
        DES_glbattr.Correction_table_name               = os.path.basename(conf.corr_file)
        DES_glbattr.Correction_table_scaling_factor =  "{:0.5f}".format(sf_des)
        DES_glbattr.Energy_table_name               =  conf.energyfile
        #DES_glbattr.Lower_energy_integration_limit = "{:02f}".format(corrTable[inp['mode'] + 'lowIntegLimit'])
        #DES_glbattr.Upper_energy_integration_limit = "{:02f}".format(corrTable[inp['mode'] + 'highIntegLimit'])
        DES_glbattr.Dead_time_correction = str(math.ceil(conf.effective_deadtime / 1e-9)) + ' ns'
        #DES_glbattr.Magnetic_field_filenames = srvy_fnames
        DES_glbattr.skymap_avgN = corrTable['skymap_avgN']
        if usec_searchfile != None and os.path.exists(usec_searchfile):
            DES_glbattr.Microsecond_offset_filename = os.path.basename(usec_searchfile)

    '''
    glb attrs needed for L1A:
    Data_version: 3.4.0, 0.0.0
    Logical_file_id: mms1_fpi_fast_l1a_des-cnts_20171221020000_v3.4.0, mms1_fpi_fast_l1a_des-cnts_00000000000000_v0.0.0
    Generation_date: Mon Oct 17 15:45:17 2022, 20151102
     '''
    def populate_global_attrs(self, myDES_L1A):

        myDES_L1A.Generation_date =                self.Generation_date
        myDES_L1A.Logical_file_id =                self.Logical_file_id.replace(".cdf","")
        myDES_L1A.Data_version =                   self.Data_version

    '''
    POPULATE GLOBAL ATTRIBUTES
    '''

    def slow_survey_DES(DES_gblattr,corrTable, conf, MG, MGB,
                        sc_pot, photo_model,PKT_SECHDREXID):
        luts = corrTable['photomodel_luts']
        cfile = "_".join([conf.sc_id , conf.mode, 'f1ct', corrTable["tag_des"] ,
                          'p' + corrTable["etag_des1"] + '.txt'])

        # BURST uses both brst magnetic field files and fast srvy magnetic field files
        magfield_filenames = ((str(MG.srvy_basenames).replace("[","")[0:-1]).replace("'","")).replace(",","")
        if MGB != None:
            brst_magfield_filenames = ((str(MGB.srvy_basenames).replace("[", "")[0:-1]).replace("'", "")).replace(",", "")
            magfield_filenames = " ".join([magfield_filenames, brst_magfield_filenames])


        energy_e0 = 100
        scp_energy_frac = 1.0
        DES_gblattr.Correction_table_name               = cfile
        DES_gblattr.Correction_table_scaling_factor    =  "{:0.5f}".format(float(luts[5]))
        #DES_gblattr.Correction_table_rev                = getfilerev(os.path.join(corrTable['pathdir'], conf.sc_id, cfile))
        correction_table_scaling_factor                 = "{:0.5f}".format(float(corrTable['sf_des']))
        DES_gblattr.Energy_table_name                   = conf.energyfile
        DES_gblattr.Dead_time_correction                = conf.effective_deadtime
        DES_gblattr.Magnetic_field_filenames            = magfield_filenames
        DES_gblattr.Spacecraft_potential_filenames      = ((str(sc_pot.scp_basenames).replace("[","")[0:-1]).replace("'","")).replace(",","")
        DES_gblattr.Photoelectron_model_filenames       =  photo_model.fname
        DES_gblattr.Photoelectron_model_scaling_factor  =  "{:0.7f}".format(float(luts[5]))
        if conf.use_pfilter:
            DES_gblattr.Photoelectron_filter                = "On"
        else:
            DES_gblattr.Photoelectron_filter                = "Off"
        DES_gblattr.Lower_energy_integration_limit      = "{:0.2f}eV".format(float(corrTable["deslowIntegLimit"]))
        DES_gblattr.Upper_energy_integration_limit      = "{:0.2f}eV".format(float(corrTable["deshighIntegLimit"]))
        DES_gblattr.Energy_e0                           =  "{:0.2f}eV".format(energy_e0)  # from orbit_constants
        DES_gblattr.Scp_energy_fraction                 = "{:0.2f}eV".format(scp_energy_frac)
        DES_gblattr.skymap_avgN                         =  corrTable['skymap_avgN']
        DES_gblattr.Quadrant                            = PKT_SECHDREXID & 3
        DES_gblattr.High_energy_extrapolation           = 'Enabled' # as this is always true
        try:
            DES_gblattr.Low_energy_extrapolation = (['Disabled', 'Enabled'])[DES_gblattr.lo_ext]
        except TypeError:
            pass

    # These files are obtained only during processing...
    def build_attitude(self,defatt_filenames_obtained_from_dbcs):
        # This file changes every time a day boundary is crossed and a new transform is needed (every 10 min)
        for file in defatt_filenames_obtained_from_dbcs:
            if file != None:
                if self.Spacecraft_attitude_filenames.find(os.path.basename(file)) < 0:
                      self.Spacecraft_attitude_filenames = self.Spacecraft_attitude_filenames + " " +  \
                      os.path.basename(file)

    def slow_survey_DIS(DIS_gblattr,corrTable, conf,
                        MG, MGB, sc_pot, photo_model, PKT_SECHDREXID):
        cfile =  "_".join([conf.sc_id, conf.mode,'f1ct',  corrTable["tag_dis"], 'p' + corrTable["etag_dis1"]]) + '.txt'
        luts = corrTable['photomodel_luts']
        energy_e0 = 100
        scp_energy_frac = 1.0
        DIS_gblattr.Correction_table_name = cfile
        DIS_gblattr.Correction_table_scaling_factor = "{:0.5f}".format(float(corrTable['sf_dis']))
        #DIS_gblattr.Correction_table_rev = getfilerev(os.path.join(corrTable['pathdir'], conf.sc_id, cfile))
        correction_table_scaling_factor = "{:0.5f}".format(float(corrTable['sf_dis']))
        DIS_gblattr.Energy_table_name = conf.energyfile
        DIS_gblattr.Dead_time_correction = conf.effective_deadtime
        DIS_gblattr.Magnetic_field_filenames = (
            (str(MG.srvy_basenames).replace("[", "")[0:-1]).replace("'", "")).replace(",", "")
        DIS_gblattr.Spacecraft_potential_filenames = (
            (str(sc_pot.scp_basenames).replace("[", "")[0:-1]).replace("'", "")).replace(",", "")
        DIS_gblattr.Photoelectron_model_filenames = photo_model.fname
        DIS_gblattr.Photoelectron_model_scaling_factor =  float(luts[5])
        DIS_gblattr.Photoelectron_filter  =  conf.use_pfilter
        DIS_gblattr.Lower_energy_integration_limit = "{:0.2f}eV".format(float(corrTable["dislowIntegLimit"]))
        DIS_gblattr.Upper_energy_integration_limit = "{:0.2f}eV".format(float(corrTable["dishighIntegLimit"]))

        DIS_gblattr.Energy_e0 =  "{:0.2f}eV".format(energy_e0) # from orbit_constants
        DIS_gblattr.Scp_energy_fraction = "{:0.2f}eV".format(scp_energy_frac)
        DIS_gblattr.skymap_avgN = corrTable['skymap_avgN']
        DIS_gblattr.Quadrant = PKT_SECHDREXID & 3
        DIS_gblattr.High_energy_extrapolation = 'Enabled'
        DIS_gblattr.Spacecraft_attitude_filenames = ''  # updated in map loop
        DIS_gblattr.High_energy_extrapolation           = 'Enabled' # as this is always true
        try:
            DIS_gblattr.Low_energy_extrapolation = (['Disabled', 'Enabled'])[DIS_gblattr.lo_ext]
        except TypeError:
            pass