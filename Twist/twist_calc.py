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

def change_of_twist_angle():






# Height of the middle spar based on imported value
wingbox_corner_points = database_connector.load_wingbox_value("wingbox_corner_points")
wingbox_centroid_location = database_connector.load_wingbox_value("wingbox_centroid_location")

def spar_positions(wingbox_corner_points, wingbox_centroid_location):
    # x position of the spar
    x_spar = wingbox_centroid_location[0]

    # y position of the spar
    y_top = min(wingbox_corner_points[0][1], wingbox_corner_points[1][1])

    slope_bottom_surface = (wingbox_corner_points[3][1] - wingbox_corner_points[2][1]) / \
                           (wingbox_corner_points[3][0] - wingbox_corner_points[2][0])
    y_bottom = x_spar * slope_bottom_surface

    return [(x_spar, y_top), (x_spar, y_bottom)]


def rewriting_wingbox_corner_points(wingbox_corner_points, spar_positions):
    """Making a new wingbox list with the spar's points inserted in clockwise order"""

    updated_wingbox_coordinates = [wingbox_corner_points[0],spar_positions[0], wingbox_corner_points[1]
        , wingbox_corner_points[2],spar_positions[1], wingbox_corner_points[3]]

    database_connector.save_wingbox_value("wingbox_corner_points_with_spar", updated_wingbox_coordinates)
    database_connector.commit_to_database()

    return




# Torsional constant calculation
def J_y(d_theta_d_y, G, T_y):
    J_y = (T_y) / (d_theta_d_y * G)
    return J_y

def J_value(J_y, y_position):
    J_@y = (J_y * y_position)
    return J_@y