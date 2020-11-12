import numpy as np
import scipy as sp
from scipy import interpolate
from Database.database_functions import DatabaseConnector
import os
import inspect
database_connector = DatabaseConnector()

aerodynamic_data_file_0 = '\MainWing_a0.00_v10.00ms.txt'
aerodynamic_data_file_10 = '\MainWing_a10.00_v10.00ms.txt'


"""
Output of this function is a numpy array, where [1] is the second data point etc. In that data point:
[0] is the y-span, [1] is the chord, [2] the induced angle of attack, [3] the Cl, [5] the induced Cd, [7] is Cm around c/4
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

"""
Y-span varies from 0 to 
"""
chord_function = sp.interpolate.interp1d(aerodynamic_data_0[:, 0], aerodynamic_data_0[:, 1], kind='cubic', fill_value="extrapolate")

# 0 aoa
angle_induced_function_0 = sp.interpolate.interp1d(aerodynamic_data_0[:, 0], aerodynamic_data_0[:, 2], kind='cubic', fill_value="extrapolate")
lift_coef_function_0 = sp.interpolate.interp1d(aerodynamic_data_0[:, 0], aerodynamic_data_0[:, 3], kind='cubic', fill_value="extrapolate")
drag_induced_function_0 = sp.interpolate.interp1d(aerodynamic_data_0[:, 0], aerodynamic_data_0[:, 4], kind='cubic', fill_value="extrapolate")
moment_coef_function_0 = sp.interpolate.interp1d(aerodynamic_data_0[:, 0], aerodynamic_data_0[:, 5], kind='cubic', fill_value="extrapolate")

# 10 aoa
angle_induced_function_10 = sp.interpolate.interp1d(aerodynamic_data_10[:, 0], aerodynamic_data_10[:, 2], kind='cubic', fill_value="extrapolate")
lift_coef_function_10 = sp.interpolate.interp1d(aerodynamic_data_10[:, 0], aerodynamic_data_10[:, 3], kind='cubic', fill_value="extrapolate")
drag_induced_function_10 = sp.interpolate.interp1d(aerodynamic_data_10[:, 0], aerodynamic_data_10[:, 4], kind='cubic', fill_value="extrapolate")
moment_coef_function_10 = sp.interpolate.interp1d(aerodynamic_data_10[:, 0], aerodynamic_data_10[:, 5], kind='cubic', fill_value="extrapolate")