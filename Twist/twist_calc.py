import numpy as np
import scipy as sp

try:
    from Database.database_functions import DatabaseConnector
    from WingData.chord_function import chord_function
    # from WingboxCreator.wingbox_creator import wingbox_area, wingbox_line
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    from WingData.chord_function import chord_function
    # from WingboxCreator.wingbox_creator import wingbox_area, wingbox_line

database_connector = DatabaseConnector()

G = database_connector.load_wingbox_value("shear_modulus_Pa")
t1 = database_connector.load_wingbox_value("...")
t3 = database_connector.load_wingbox_value("...")
wingbox_points = database_connector.load_wingbox_value("wingbox_corner_points")
b1 = wingbox_points[0][1] - wingbox_points[3][1]
b2 = wingbox_points[1][1] - wingbox_points[2][1]
b3 = 0
a1 = 0
a2 = 0
c1 = 0
c2 = 0
A1 = 0.5 * (b1+b3)(wingbox_points[.][.]-wingbox_points[0][0])
A2 = 0.5 * (b2+b3)(wingbox_points[1][0]-wingbox_points[.][.])

# Matrix of the shear flow and change of angle. 1st variable is q1 second is q2 third is dThetha/dy.
def change_of_twist_angle(y):
    matrix = np.array([[2*A1*chord_function(y)*chord_function(y), 2*A2chord_function(y)*chord_function(y), 0], 
                [(((((b1+a1+a2)*chord_function(y))/t1)+(b3*chord_function(y)/t3))/2*A1*chord_function(y)*chord_function(y)*G), -((b3*chord_function(y)/t3)/2*A1*chord_function(y)*chord_function(y)*G), -1], 
                [-((b3*chord_function(y)/t3)/2*A2*chord_function(y)*chord_function(y)*G), (((((b2+c1+c2)*chord_function(y))/t1)+(b3*chord_function(y)/t3))/2*A2*chord_function(y)*chord_function(y)*G), -1]])
    solution_vector = np.array([TorquePlaceHolder(), 0, 0])
    return np.linalg.solve(matrix, solution_vector)


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
    y_bottom = x_spar * slope_bottom_surface + wingbox_corner_points[3][1]

    return [(x_spar, y_top), (x_spar, y_bottom)]


def rewriting_wingbox_corner_points(wingbox_corner_points, spar_positions):
    """Making a new wingbox list with the spar's points inserted in clockwise order"""

    updated_wingbox_coordinates = [wingbox_corner_points[0], spar_positions[0], wingbox_corner_points[1]
        , wingbox_corner_points[2], spar_positions[1], wingbox_corner_points[3]]

    database_connector.save_wingbox_value("wingbox_corner_points_with_spar", updated_wingbox_coordinates)
    database_connector.commit_to_wingbox_definition()

    return


# Torsional constant calculation
def J_y(d_theta_d_y, G, T_y):
    J_y = (T_y) / (d_theta_d_y * G)
    return J_y

# def J_value(J_y, y_position):
# J_@y = (J_y * y_position)
# return J_@y
