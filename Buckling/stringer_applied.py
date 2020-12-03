from math import *

try:
    from Database.database_functions import DatabaseConnector
    from IntertialLoadingCalculator.inertial_loading_calculator import drag_distribution
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    from IntertialLoadingCalculator.inertial_loading_calculator import z_final_force_distribution, lift_distribution

database_connector = DatabaseConnector()

Ixx = database_connector.load_wingbox_value("")
Izz = database_connector.load_wingbox_value("")

try:
    with open("../InertialLoadingCalculator/data.pickle", 'rb') as file:
        data = pickle.load(file)
except FileNotFoundError:
    with open("./data.pickle", 'rb') as file:
        data = pickle.load(file)

spanwise_locations_list = data[0]
x_moment_data = data[3]
x_moment_func = sp.interpolate.interp1d(spanwise_locations_list, x_moment_data, kind="cubic", fill_value="extrapolate")
global_step_length = spanwise_locations_list[1] - spanwise_locations_list[0]


def moment_lift():
    lift_distribution

def moment_drag():
    drag_distribution


def normal_stress_stringer(moment_lift, moment_drag, z_location, x_location):
    sigma_stringer = (moment_lift*z_location)/Ixx + (moment_drag*x_location)/Izz