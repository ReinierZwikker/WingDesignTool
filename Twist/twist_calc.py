import numpy as np
import scipy as sp
from scipy import integrate
from math import *

try:
    from Database.database_functions import DatabaseConnector
    from WingData.chord_function import chord_function
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    from WingData.chord_function import chord_function

database_connector = DatabaseConnector()

G = database_connector.load_wingbox_value("shear_modulus_pa")
t1 = 0.003  # database_connector.load_wingbox_value("...")
t3 = 0.003  # database_connector.load_wingbox_value("...")

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


# Matrix of the shear flow and change of angle. 1st variable is q1 second is q2 third is dThetha/dy.
def rate_twist(y):
    chord = chord_function(y)
    matrix = np.array([[2 * Area_first * chord * chord, 2 * Area_second * chord * chord, 0],
                       [(((((b_one + a_one + a_two) * chord) / t1) + (b_three * chord / t3)) / (2 * Area_first * chord * chord * G)),
                        -1 * ((b_three * chord / t3) / (2 * Area_first * chord * chord * G)), -1],
                       [-1 * ((b_three * chord / t3) / (2 * Area_second * chord * chord * G)),
                        (((((b_two + c_one + c_two) * chord / t1) + (b_three * chord / t3)) / (2 * Area_second * chord * chord * G))), -1]])
    solution_vector = np.array([50000, 0, 0])  # TorquePlaceHolder() in first array slot
    q1, q2, d_theta = np.linalg.solve(matrix, solution_vector)
    return d_theta


def twist_angle_rad():
    estimate, error = sp.integrate.quad(rate_twist, 0, database_connector.load_value("halfspan"))
    return estimate


def twist_angle_deg():
    return twist_angle_rad() * 180 / pi


# def stiffness(y):
# return TorquePlaceHolder()/ rate_twist(y) * G

print(twist_angle_deg())
