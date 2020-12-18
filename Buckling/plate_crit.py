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
kc = 7.3
t = database_connector.load_wingbox_value("plate_thickness")
points = database_connector.load_wingbox_value("wingbox_corner_points")
top_lim1 = database_connector.load_wingbox_value("top_stringer_lim_point_1")
top_lim2 = database_connector.load_wingbox_value("top_stringer_lim_point_2")
top_num_1 = database_connector.load_wingbox_value("top_number_of_stringers_1")
top_num_2 = database_connector.load_wingbox_value("top_number_of_stringers_2")
top_num_3 =database_connector.load_wingbox_value("top_number_of_stringers_3")
bot_lim1 = database_connector.load_wingbox_value("bottom_stringer_lim_point_1")
bot_lim2 = database_connector.load_wingbox_value("bottom_stringer_lim_point_2")
bot_num_1 = database_connector.load_wingbox_value("bottom_number_of_stringers_1")
bot_num_2 = database_connector.load_wingbox_value("bottom_number_of_stringers_2")
bot_num_3 =database_connector.load_wingbox_value("bottom_number_of_stringers_3")



def stringer_spacing(y):
    if y <= top_lim1:
        spacing = (sqrt((points[1][0] - points[0][0])**2 + (points[1][1] - points[0][1])**2) * chord_function(y)) / (top_num_1+2)
    if top_lim1 < y <= top_lim2:
        spacing = (sqrt((points[1][0] - points[0][0])**2 + (points[1][1] - points[0][1])**2) * chord_function(y)) / (top_num_2+1)
    else:
        spacing = (sqrt((points[1][0] - points[0][0])**2 + (points[1][1] - points[0][1])**2) * chord_function(y)) / (top_num_3+1)
     
    return spacing

def stringer_spacing_bottom(y):
    if y <= bot_lim1:
        spacing = (sqrt((points[1][0] - points[0][0])**2 + (points[1][1] - points[0][1])**2) * chord_function(y)) / (bot_num_1+2)
    if bot_lim1 < y <= bot_lim2:
        spacing = (sqrt((points[1][0] - points[0][0])**2 + (points[1][1] - points[0][1])**2) * chord_function(y)) / (bot_num_2+1)
    else:
        spacing = (sqrt((points[1][0] - points[0][0])**2 + (points[1][1] - points[0][1])**2) * chord_function(y)) / (bot_num_3+1)
    return spacing

def plate_crit_stress(y, mode='top'): #Kc needs to be determined manually per section
    if mode == 'top':
        Fcr = (((pi**2)*kc*E) / (12*(1-(pois**2)))) * ((t/stringer_spacing(y))**2)
    if mode == 'bottom':
        Fcr = (((pi**2)*kc*E) / (12*(1-(pois**2)))) * ((t/stringer_spacing_bottom(y))**2)
    return Fcr