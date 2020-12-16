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

pois = database_connector.load_wingbox_value("poisson_ratio")
E = database_connector.load_wingbox_value("youngs_modulus_pa")
ks = 0 #Might vay per section. Ks need to be determined manually per section
t = database_connector.load_wingbox_value("spar_thickness")
points = database_connector.load_wingbox_value("wingbox_corner_points")


def spar_crit_stress(y): #b is the height of the spar
    b = (points[1][1] - points[2][1]) * chord_function(y)
    stress = (((pi**2)*ks*E) / (12*(1-(pois**2)))) * ((t/b)**2)
    return stress 