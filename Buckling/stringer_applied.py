import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import pickle

try:
    from Integrator import Integration
    from Database.database_functions import DatabaseConnector
    from MOIcalc.moicalc import inertia
    from CentroidCalculator.centroid_calculator import get_centroid
    from WingData.chord_function import chord_function
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    from Integrator import Integration
    from MOIcalc.moicalc import inertia
    from CentroidCalculator.centroid_calculator import get_centroid
    from WingData.chord_function import chord_function

database_connector = DatabaseConnector()

try:
    with open("../InertialLoadingCalculator/data.pickle", 'rb') as file:
        data = pickle.load(file)
except FileNotFoundError:
    with open("./data.pickle", 'rb') as file:
        data = pickle.load(file)

y_lst = data[0]
x_moment_lst = data[3]
z_moment_lst = data[6]
step = y_lst[1] - y_lst[0]
b = database_connector.load_value("wing_span")/2
wingbox_points = database_connector.load_wingbox_value("wingbox_corner_points")

x_moment = sp.interpolate.interp1d(y_lst, x_moment_lst, kind="cubic", fill_value="extrapolate")
z_moment = sp.interpolate.interp1d(y_lst, z_moment_lst, kind="cubic", fill_value="extrapolate")


#normal stress stringers due to bending
def string_stress_normal(y):
    M_z = z_moment(y)
    M_x = x_moment(y)
    I = inertia(y)
    I_zz = I[1]
    I_xx = I[0]
    I_xz = 0
    centroid = get_centroid(y)
    wingbox_point = [i * chord_function(y) for i in wingbox_points[1]]
    x = wingbox_point[0] - centroid[0]
    z = wingbox_point[1] - centroid[1]
    sigma = ((((M_x*I_zz)-(M_z*I_xz))*z)+(((M_z*I_xx)-(M_x*I_xz))*x))/((I_xx*I_zz)-(I_xz)**2)
    return sigma

print(string_stress_normal(0))