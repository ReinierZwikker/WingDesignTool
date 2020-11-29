import numpy as np
import scipy as sp
from scipy import integrate, interpolate
from math import *
import pickle
import matplotlib.pyplot as plt

try:
    from Database.database_functions import DatabaseConnector
    from WingData.chord_function import chord_function
    from Integrator import Integration
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    from WingData.chord_function import chord_function
    from Integrator import Integration

database_connector = DatabaseConnector()

G = database_connector.load_wingbox_value("shear_modulus_pa")
t1 = 0.003  # database_connector.load_wingbox_value("...") left and right spar
t2 = 0.003  # database_connector.load_wingbox_value("...") skin
t3 = 0.003  # database_connector.load_wingbox_value("...") mid spar
engine_pos = database_connector.load_value("engine_spanwise_location")


wingbox_points = database_connector.load_wingbox_value("wingbox_points")

b_one = (wingbox_points[0][1] - wingbox_points[5][1])
b_two = (wingbox_points[2][1] - wingbox_points[3][1])
b_three = (wingbox_points[1][1] - wingbox_points[4][1])
a_one = sqrt((wingbox_points[0][1] - wingbox_points[1][1]) ** 2 + (wingbox_points[1][0] - wingbox_points[0][0]) ** 2)
a_two = sqrt((wingbox_points[4][1] - wingbox_points[5][1]) ** 2 + (wingbox_points[4][0] - wingbox_points[5][0]) ** 2)
c_one = sqrt((wingbox_points[1][1] - wingbox_points[2][1]) ** 2 + (wingbox_points[1][0] - wingbox_points[2][0]) ** 2)
c_two = sqrt((wingbox_points[3][1] - wingbox_points[4][1]) ** 2 + (wingbox_points[3][0] - wingbox_points[4][0]) ** 2)
Area_first = 0.5 * (b_one + b_three) * (wingbox_points[1][0] - wingbox_points[0][0])
Area_second = 0.5 * (b_two + b_three) * (wingbox_points[2][0] - wingbox_points[1][0])
Area_single = 0.5 * (b_one + b_two) * (wingbox_points[2][0] - wingbox_points[0][0])

try:
    with open("./data.pickle", 'rb') as file:
        data = pickle.load(file)
except FileNotFoundError:
    with open("../InertialLoadingCalculator/data.pickle", 'rb') as file:
        data = pickle.load(file)


y_span_lst = data[0]
torsion_lst = data[7]
step = y_span_lst[1] - y_span_lst[0]
    
torsion = sp.interpolate.interp1d(y_span_lst, torsion_lst, kind="cubic", fill_value="extrapolate")


# Matrix of the shear flow and change of angle. 1st variable is q1 second is q2 third is dThetha/dy.
def dtheta_multi(y):
    chord = chord_function(y)
    matrix = np.array([[2 * Area_first * chord * chord, 2 * Area_second * chord * chord, 0],
                       [(((((a_one + a_two) * chord) / t2) + (b_one * chord / t1) + (b_three * chord / t3)) / (2 * Area_first * chord * chord * G)),
                        -1 * ((b_three * chord / t3) / (2 * Area_first * chord * chord * G)), -1],
                       [-1 * ((b_three * chord / t3) / (2 * Area_second * chord * chord * G)),
                        (((((c_one + c_two) * chord / t2) + (b_two * chord / t1) + (b_three * chord / t3)) / (2 * Area_second * chord * chord * G))), -1]])
    solution_vector = np.array([torsion(y), 0, 0])
    q1, q2, dtheta = np.linalg.solve(matrix, solution_vector)
    return dtheta


def single_cell_stiffness(y):
    chord = chord_function(y)
    line_int = ((a_one+c_one+a_two+c_two)*chord)/t2 + ((b_one+b_two)*chord)/t1
    return (4*((Area_second*chord*chord)**2))/line_int


def dtheta_single(y):
    return torsion(y)/(G*single_cell_stiffness(y))


def rate_of_twist(y):
    if y <= engine_pos:
        return dtheta_multi(y)
    else:
        return dtheta_single(y)


def twist_lst_deg():
    twist_integral = Integration(rate_of_twist, database_connector.load_value("wing_span") / 2, 0, flip_sign=True)
    twist_lst = []
    for i in y_span_lst:
        twist_lst.append(twist_integral.integrate(i, -1*step))
    return [x*180/pi for x in twist_lst]


#def twist_angle_rad():
    #estimate, error = sp.integrate.quad(rate_twist, 0, database_connector.load_value("wing_span")/2)
    #return estimate


#def twist_angle_deg():
    #return twist_angle_rad() * 180 / pi


def stiffness(y):
    return torsion(y) / (dtheta_multi(y) * G)


def stiffness_lst():
    lst = []
    for i in y_span_lst:
        if i <= engine_pos:
            lst.append(stiffness(i))
        if i > engine_pos:
            lst.append(single_cell_stiffness(i))
    return lst

"""
print(stiffness_lst())
print(twist_angle_deg())
print(min(twist_lst_deg()))

plt.plot(y_span_lst, twist_lst_deg())
plt.show()
"""

print(stiffness_lst())
print(dtheta_single(11))

plt.plot(y_span_lst, stiffness_lst())
plt.show()
