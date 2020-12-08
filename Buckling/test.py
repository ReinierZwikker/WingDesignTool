import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import pickle

try:
    from Integrator import Integration
    from Database.database_functions import DatabaseConnector
    from MOIcalc.moicalc import inertia
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    from Integrator import Integration
    from MOIcalc.moicalc import inertia

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

x_moment = sp.interpolate.interp1d(y_lst, x_moment_lst, kind="cubic", fill_value="extrapolate")
z_moment = sp.interpolate.interp1d(y_lst, z_moment_lst, kind="cubic", fill_value="extrapolate")


#normal stress stringers due to bending
def string_stress_normal(bl):
    M_z = z_moment(y)
    M_x = x_moment(y)
    I = inertia(y)
    I_zz = I[1]
    I_xx = I[0]
    I_xz = 0
    x = #max distance to centroid
    z = #max distance to centroid
    sigma = ((((M_x*I_zz)-(M_z*I_xz))*z)+(((M_z*I_xx)-(M_x*I_xz))*x))/((I_xx*I_yy)-(I_xz)**2)
    return sigma

while i <= hb:
    applied_stress = string_stress_normal(i)
    string_stress_normal_list.append(applied_stress)
    mos = margin_of_safety(applied_stress)
    mos_list.append(mos)
    i += step