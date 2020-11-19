import numpy as np
import scipy as sp

try:
    from Database.database_functions import DatabaseConnector
    # from WingboxCreator.wingbox_creator import wingbox_area, wingbox_line
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    # from WingboxCreator.wingbox_creator import wingbox_area, wingbox_line

database_connector = DatabaseConnector()

wingbox_points = database_connector.load_value()
b1 = 

# Matrix of the shear flow and change of angle. 1st variable is q1 second is q2 third is dThetha/dy.
"""Niet voor Watjes"""
def change_of_twist_angle():






# Height of the middle spar based on imported value
wingbox_corner_points = database_connector.load_wingbox_value("wingbox_corner_points")
wingbox_centroid_location = database_connector.load_wingbox_value("wingbox_centroid_location")

def spar_positions(wingbox_corner_points, wingbox_centroid_location):




# Torsional constant calculation
def J_y(d_theta_d_y, G, T_y):
    J_y = (T_y) / (d_theta_d_y * G)
    return J_y

def J_value(J_y, y_position):
    J_@y = (J_y * y_position)
    return J_@y