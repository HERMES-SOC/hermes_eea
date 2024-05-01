import hermes_eea.calibration as calib
from pathlib import Path
import hermes_eea
from hermes_eea.io import read_file
import os


class Stepper_Table():

    def __init__(self, stepper_table: Path):
        self.stepper_table_file = os.path.join(hermes_eea._calibration_directory, stepper_table)
        self.parse_stepper_table()
        self.n_defl     = len(get_unique_list(self.deflections))
        self.n_energies = len(get_unique_list(self.energies))
     
        self.v_defl = [
          -16.875,
          -5.625,
          5.625,
          16.875
        ]
      
        self.v_energies = [
          2.18000000e00,
          2.63177330e00,
          3.17717004e00,
          3.83559233e00,
          4.63046306e00,
          5.59005918e00,
          6.74851766e00,
          8.14704980e00,
          9.83540739e00,
          1.18736525e01,
          1.43342944e01,
          1.73048684e01,
          2.08910507e01,
          2.52204172e01,
          3.04469818e01,
          3.67566761e01,
          4.43739626e01,
          5.35698211e01,
          6.46713874e01,
          7.80735920e01,
          9.42532085e01,
          1.13785815e02,
          1.37366271e02,
          1.65833433e02,
          2.00200000e02,
          2.39800000e02,
          3.17794829e02,
          4.21157437e02,
          5.58138682e02,
          7.39673007e02,
          9.80251281e02,
          1.29907752e03,
          1.72160182e03,
          2.28155195e03,
          3.02362557e03,
          4.00705827e03,
          5.31035195e03,
          7.03754125e03,
          9.32649800e03,
          1.23599368e04,
          1.63800000e04,
        ]
   
    def parse_stepper_table(self):
        """
        Given a calibration, return the calibration structure.
    
        Parameters
        ----------
        DJG says that energies and angles may change
        calib_filename: str
            Fully specificied filename of the non-calibrated file (data level < 2)
            0 1
        Returns
        -------
        output_filename: str
            Fully specificied filename of the appropriate calibration file.
    
        Examples
        --------
        """
        
        lines = read_file(os.path.join(self.stepper_table_file))
        self.energies = []
        self.deflections = []
        for line in lines:
            self.energies.append(int(line[8:10], 16))
            self.deflections.append(int(line[10:12], 16))
         
         
def get_unique_list(arr):   
 
    unique_list = []

    for x in arr:
        if x not in unique_list:
            unique_list.append(x)    
    return unique_list