import json
import sys
import os
import inspect
from os import path
import scipy as sp
from scipy import interpolate
import numpy as np

try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector

# Init database connection
database_connector = DatabaseConnector()

# Locate wingbox file destination
wingbox_creator_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
wingbox_file_destination = wingbox_creator_folder.replace("\\", "/").removesuffix("/WingboxCreator") + '/Database/wingbox.json'

halfspan = database_connector.load_value("wing_span") / 2
quarter_chord_sweep = database_connector.load_value("quarter_chord_sweep")
dihedral_angle = database_connector.load_value("dihedral_angle")

""" Determination of the wingbox coordinates """


def airfoil_definition_converter(airfoil_file):  # Previously 'text_to_array_converter'
    # the x and y are arranged vertically
    a_foil_array_1_top_surface = np.genfromtxt(airfoil_file, skip_header=1, skip_footer=100, usecols=(0, 1))
    a_foil_array_1_bottom_surface = np.genfromtxt(airfoil_file, skip_header=101, usecols=(0, 1))

    # the x and y are arranged horizontally
    a_foil_array_2_top_surface = [a_foil_array_1_top_surface[:, 0], a_foil_array_1_top_surface[:, 1]]
    a_foil_array_2_bottom_surface = [a_foil_array_1_bottom_surface[:, 0], a_foil_array_1_bottom_surface[:, 1]]

    return a_foil_array_2_top_surface, a_foil_array_2_bottom_surface


def value_finder(spar_lst, a_foil_array):  # I know it is not the pretties but it is easy to read, forgive me

    wingbox_vertices = []

    for n in range(0, 2):
        for x in spar_lst:
            y = round(float(sp.interpolate.interp1d(a_foil_array[n][0], a_foil_array[n][1], kind="cubic",
                                                    fill_value="extrapolate")(x)), 4)
            wingbox_vertices.append((x, y))

    # arrange them such that the 1st is the top left corner and the other follow in clockwise direction
    wingbox_vertices = [wingbox_vertices[0], wingbox_vertices[1], wingbox_vertices[3], wingbox_vertices[2]]

    return wingbox_vertices


def get_wingbox_corner_points(airfoil_file, spar_lst):
    wingbox_vertices = value_finder(spar_lst, airfoil_definition_converter(airfoil_file))

    return wingbox_vertices


# file position data
file_name = "./NACA_2412_many_points_plot.txt"  # the number of points generated is 201

# spar position data
spar_pos = [0.15, 0.60]

wingbox_corner_points = get_wingbox_corner_points(wingbox_creator_folder + file_name, spar_pos)


# Saving all definitions of the wingbox to a dict
wingbox_definition = {'length': halfspan,
                      'height': 0.2,
                      'wingbox_corner_points': wingbox_corner_points,  # as a function of chord and total height?
                      'quarter_chord_sweep': quarter_chord_sweep,
                      'dihedral_angle': dihedral_angle,
                      'stringers_top': [0.1, 0.2, 0.5, 0.7, 0.9],
                      # Stringer location from LE to TE as fraction of wingbox width
                      'stringers_bottom': [0.1, 0.2, 0.5, 0.7, 0.9],
                      # Stringer location from LE to TE as fraction of wingbox width
                      'stringers_leading': [0.2, 0.5, 0.7],
                      # Stringer location from bottom to top as fraction of wingbox height
                      'stringers_trailing': [0.2, 0.5, 0.7],
                      # Stringer location from bottom to top as fraction of wingbox height
                      'ribs': [0.1, 0.2, 0.5, 0.7, 0.9],  # Rib location from root to tip as fraction of wingbox length
                      'stiffeners': [0.1, 0.2, 0.3, 0.5, 0.6, 0.7, 0.9],
                      # Stiffener location from root to tip as fraction of wingbox length
                      'sheet_thickness': 0.1,
                      'stringer_thickness': 0.1,
                      'rib_thickness': 0.1,
                      'stiffener_thickness': 0.1
                      }

# Saving the dict to a file
with open(wingbox_file_destination, "w") as wingbox_database:
    json.dump(wingbox_definition, wingbox_database, indent=4)
