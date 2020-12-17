from math import *
import pickle
import scipy as sp
from scipy import integrate, interpolate

try:
    from Database.database_functions import DatabaseConnector
    from CentroidCalculator.centroid_calculator import get_centroid
    import Importer.xflr5 as aerodynamic_data
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    from CentroidCalculator.centroid_calculator import get_centroid
    import Importer.xflr5 as aerodynamic_data


database_connector = DatabaseConnector()

#T_num_strg = #number of stringers top
#B_num_strg = #number of stringers bottom
#Area_strg = #Area of stringer 


# Import shearforce
try:
    with open("./data.pickle", 'rb') as file:
        data = pickle.load(file)
except FileNotFoundError:
    with open("../InertialLoadingCalculator/data.pickle", 'rb') as file:
        data = pickle.load(file)

"""
Sign-convention:
x: towards nose
y: towards tip
z: upwards
counterclockwise
"""

y_span_lst = data[0]
x_shear_lst = data[5]  
z_shear_lst = data[2]
torsion_lst = data[7]
step = y_span_lst[1] - y_span_lst[0]

x_shear = sp.interpolate.interp1d(y_span_lst, x_shear_lst, kind="cubic", fill_value="extrapolate")
z_shear = sp.interpolate.interp1d(y_span_lst, z_shear_lst, kind="cubic", fill_value="extrapolate")
torsion = sp.interpolate.interp1d(y_span_lst, torsion_lst, kind="cubic", fill_value="extrapolate")


# Enclosed Area
def area_segments(p):
    return zip(p, p[1:] + [p[0]])

def get_lenghts(list_coordinates):

    lenghts = [] 

    for i in range(4):
        k = i + 1
        if k >= 4:
            k = 0
        else:
            pass

        len = sqrt((list_coordinates[k][0]-list_coordinates[i][0])**2+(list_coordinates[k][1]-list_coordinates[i][1])**2)
        lenghts.append(len)
        i = i + 1 
        #  0Top plate , 1TE spar , 2bottom plate , 3front spar (not adjusted for ac)

    return lenghts

#unit slopes
def get_slopes(list_coordinates):

    slopes=[]

    for i in range(4):
        k = i + 1
        if k >= 4:
            k = 0
        else:
            pass

        if list_coordinates[k][0]==list_coordinates[i][0] or list_coordinates[k][1]==list_coordinates[i][1]:
            slopes.append(0)
            i = i+1
        else:

            slope = (list_coordinates[k][1]-list_coordinates[i][1])/(list_coordinates[k][0]-list_coordinates[i][0])
            slopes.append(slope)
            i = i+1

    return slopes

#print(lenghts)
#print(slopes)
#______________________________________________________
def AC_lenght(location):
    # Wing properties: (from the sheet)

    b = database_connector.load_value("wing_span")
    t_c = database_connector.load_value("thickness_to_chord_ratio")
    lambd = database_connector.load_value("taper_ratio")
    Cr = database_connector.load_value("root_chord")
    Ct = database_connector.load_value("tip_chord")

    hb = b / 2  # half span

    # trapezoid wing ->

    tan_alpha_wing = (Cr - Ct) / (2 * hb)  # angle between b and side of a trapezoid
    AC = Ct + (2 * tan_alpha_wing * (hb - location))
    return AC

# spars 
#3 spars 
#2 spars 
def get_t_avg( h1, h2, h3, t, lenghts, z_shear, AC, centroid, list_coordinates, slopes):

    # M_SP_LEN = (F_SP.LEN - (F_SP.LEN - B_SP.LEN) + ((x2 - x) * math.tan(B_PL.ANGL) * AC))
    x2 = list_coordinates[1][0]
    x = centroid[0]

    h_front_spar = lenghts[3]*AC
    h_back_spar = lenghts[1]*AC
    h_middle_spar = (h_front_spar - (h_front_spar-h_back_spar) + ((x2 - x)*tan(slopes[2] )*AC))

    if b<= 10:
        three_spars = True
    else:
        three_spars = False

    if three_spars == True:
        tau_avg = z_shear/ (t*h_front_spar + t*h_middle_spar + t*h_back_spar)
    else:
        tau_avg = z_shear/ (t*h_front_spar + t*h_back_spar)
    
    return tau_avg 

def torque_shear_flow( AC, Torsion):

    Am = 0.5 * abs(sum(x0 * y1 - x1 * y0 for ((x0, y0), (x1, y1)) in area_segments([x * aerodynamic_data.chord_function(b) for x in list_coordinates])))

    Torsion = T

    if b<= 10:
        three_spars = True
    else:
        three_spars = False

    if three_spars == True:
        q_t = 3 # write shit here

    else:
        q_t = T/2*Am

    return q_t 

def get_tau_max(q_t , tau_avg, kv, t):

    tau_max = kv* tau_avg + (q_t/t)
    return tau_max 

    



#list_coordinates = [(0.15, 0.06588533), (0.6, 0.0627513), (0.6, -0.02702924), (0.15, -0.04083288)]

#skin 