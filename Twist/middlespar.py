import numpy as np
import scipy as sp

try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

    from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()

wingbox_corner_points = database_connector.load_wingbox_value("wingbox_corner_points")
wingbox_centroid_location = [0.37216, 0.01494] #  database_connector.load_wingbox_value("wingbox_centroid_location")


def spar_positions():
    # x position of the spar
    x_spar = wingbox_centroid_location[0]

    slope_top_surface = (wingbox_corner_points[1][1] - wingbox_corner_points[0][1])/ (wingbox_corner_points[1][0] - wingbox_corner_points[0][0])
    y_top = (x_spar - wingbox_corner_points[0][0]) * slope_top_surface + wingbox_corner_points[0][1]

    slope_bottom_surface = (wingbox_corner_points[3][1] - wingbox_corner_points[2][1])/ (wingbox_corner_points[3][0] - wingbox_corner_points[2][0])
    y_bottom = (x_spar - wingbox_corner_points[3][0]) * slope_bottom_surface + wingbox_corner_points[3][1]
    
    return (x_spar, y_top), (x_spar, y_bottom)


def rewriting_wingbox_corner_points():
    """Making a new wingbox list with the spar's points inserted in clockwise order"""
    mid_spar = spar_positions()
    updated_wingbox_coordinates = [wingbox_corner_points[0], mid_spar[0], wingbox_corner_points[1]
        , wingbox_corner_points[2], mid_spar[1], wingbox_corner_points[3]]

    database_connector.save_wingbox_value("wingbox_points", updated_wingbox_coordinates)
    database_connector.commit_to_wingbox_definition()

    return

rewriting_wingbox_corner_points()