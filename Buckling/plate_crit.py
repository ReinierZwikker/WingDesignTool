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
t = database_connector.load_wingbox_value("plate_thickness")
points = database_connector.load_wingbox_value("wingbox_corner_points")
top_lim1 = database_connector.load_wingbox_value("top_stringer_lim_point_1")
top_lim2 = database_connector.load_wingbox_value("top_stringer_lim_point_2")
num_1 = database_connector.load_wingbox_value("top_number_of_stringers_1")
num_2 = database_connector.load_wingbox_value("top_number_of_stringers_2")
num_3 =database_connector.load_wingbox_value("top_number_of_stringers_3")


def stringer_spacing(y):
    if y <= top_lim1:
        spacing = (sqrt((points[1][0] - points[0][0])**2 + (points[1][1] - points[0][1])**2) * chord_function(y)) / (num_1+2)
    if top_lim1 < y <= top_lim2:
        spacing = (sqrt((points[1][0] - points[0][0])**2 + (points[1][1] - points[0][1])**2) * chord_function(y)) / (num_2+1)
    else:
        spacing = (sqrt((points[1][0] - points[0][0])**2 + (points[1][1] - points[0][1])**2) * chord_function(y)) / (num_3+1)
     
    return spacing



def plate_crit_force(y): #Kc needs to be determined manually per section
    if y < 10:
        kc = 
    Fcr = (((pi**2)*kc*E) / (12*(1-(pois**2)))) * ((t/stringer_spacing(y))**2)
    return Fcr


def plate_crit_stress(y):
    sigma = plate_crit_force(y) / (t*stringer_spacing(y))
    return sigma