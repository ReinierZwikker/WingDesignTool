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


# Torsional constant J. Takes line integral of winbox and cross-sectional area as input. Both with regards to y: span.


# Torsional constant calculation
def J_y(d_theta_d_y, G, T_y):
    J_y = (T_y) / (d_theta_d_y * G)
    return J_y

def J_value(J_y, y_position):
    J_@y = (J_y * y_position)
    return J_@y