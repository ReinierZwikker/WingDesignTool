from math import *

try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()

Ixx = database_connector.load_wingbox_value("")
Izz = database_connector.load_wingbox_value("")


def moment_lift():

def moment_drag():


def normal_stress_stringer(moment_lift, moment_drag, z_location, x_location):
    sigma_stringer = (moment_lift*z_location)/Ixx + (moment_drag*x_location)/Izz