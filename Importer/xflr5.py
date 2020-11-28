# Scroll all the way down for instructions

import numpy as np
import scipy as sp
from scipy import interpolate
import os
import inspect
try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()

aerodynamic_data_file_0 = '\MainWing_a0.00_v10.00ms.txt'
aerodynamic_data_file_10 = '\MainWing_a10.00_v10.00ms.txt'

"""
Output of this function is a numpy array, where [1] is the second data point, so in essence rows. In that data point:
[0] is the y-span, [1] is the chord, [2] the induced angle of attack, [3] the Cl, [4] the induced Cd, [5] is Cm around c/4
"""


def main_wing_xflr5(name):
    main_wing = np.genfromtxt(name, skip_header=40, skip_footer=1029, usecols=(0, 1, 2, 3, 5, 7))
    return main_wing


def rolling_moment_coef_xlfr5(name):
    with open(name, 'r') as file:
        lines = file.readlines()
        return float(lines[12].split()[2])


importer_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
aerodynamic_data_0 = main_wing_xflr5(importer_folder + aerodynamic_data_file_0)
aerodynamic_data_10 = main_wing_xflr5(importer_folder + aerodynamic_data_file_10)
rolling_moment_coef_0 = rolling_moment_coef_xlfr5(importer_folder + aerodynamic_data_file_0)
rolling_moment_coef_10 = rolling_moment_coef_xlfr5(importer_folder + aerodynamic_data_file_10)

database_connector.save_value('rolling_moment_coef_0', rolling_moment_coef_0)
database_connector.save_value('rolling_moment_coef_10', rolling_moment_coef_10)
database_connector.commit_to_database()

"""
Y-span varies from 0 to 26.78, so half span, Use the following functions as follows:
1. import this python file: import Importer.xflr5
2. If you want to know for example the chord at y = 2 location:
    xflr5.chord_function(2)
3. If you want to know for example the induced angle at the 0 angle of attack test at y = 2 location:
    xflr5.angle_induced_function_0(2)
4. If you want to know for example the lift coefficient at the 10 angle of attack test at y = 4 location:
    xflr5.lift_coef_function_10(4)
"""
chord_function = sp.interpolate.interp1d(aerodynamic_data_0[:, 0], aerodynamic_data_0[:, 1], kind='cubic', fill_value="extrapolate")

# 0 AoA
angle_induced_function_0 = sp.interpolate.interp1d(aerodynamic_data_0[:, 0], aerodynamic_data_0[:, 2], kind='cubic', fill_value="extrapolate")
lift_coef_function_0 = sp.interpolate.interp1d(aerodynamic_data_0[:, 0], aerodynamic_data_0[:, 3], kind='cubic', fill_value="extrapolate")
drag_induced_function_0 = sp.interpolate.interp1d(aerodynamic_data_0[:, 0], aerodynamic_data_0[:, 4], kind='cubic', fill_value="extrapolate")
moment_coef_function_0 = sp.interpolate.interp1d(aerodynamic_data_0[:, 0], aerodynamic_data_0[:, 5], kind='cubic', fill_value="extrapolate")

# 10 AoA
angle_induced_function_10 = sp.interpolate.interp1d(aerodynamic_data_10[:, 0], aerodynamic_data_10[:, 2], kind='cubic', fill_value="extrapolate")
lift_coef_function_10 = sp.interpolate.interp1d(aerodynamic_data_10[:, 0], aerodynamic_data_10[:, 3], kind='cubic', fill_value="extrapolate")
drag_induced_function_10 = sp.interpolate.interp1d(aerodynamic_data_10[:, 0], aerodynamic_data_10[:, 4], kind='cubic', fill_value="extrapolate")
moment_coef_function_10 = sp.interpolate.interp1d(aerodynamic_data_10[:, 0], aerodynamic_data_10[:, 5], kind='cubic', fill_value="extrapolate")
