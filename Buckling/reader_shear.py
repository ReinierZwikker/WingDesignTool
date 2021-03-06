from math import *
import pickle
from matplotlib import pyplot as plt
import numpy as np
import scipy as sp
from scipy import integrate, interpolate
import numpy as np

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
def get_t_avg(t, lenghts, z_shear, AC, centroid, list_coordinates, slopes,b):

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
        tau_avg = - z_shear/ (t*h_front_spar + t*h_middle_spar + t*h_back_spar)
    else:
        tau_avg = - z_shear/ (t*h_front_spar + t*h_back_spar)
    
    return tau_avg 

def torque_shear_flow( AC, Torsion, b, list_coordinates):

    Am = 0.5 * abs(sum(x0 * y1 - x1 * y0 for ((x0, y0), (x1, y1)) in area_segments([x * aerodynamic_data.chord_function(b) for x in list_coordinates])))



    if b<= 10:
        three_spars = True
    else:
        three_spars = False

    if three_spars == True:
        

        try:
            with open("./data.pickle", 'rb') as file:
                data = pickle.load(file)
        except FileNotFoundError:
            with open("../InertialLoadingCalculator/data.pickle", 'rb') as file:
                data = pickle.load(file)
        y_span_lst = data[0]

        # TORQUE
        spanwise_location = b
        torsion_lst = data[7]
        torsion = sp.interpolate.interp1d(y_span_lst, torsion_lst, kind="cubic", fill_value="extrapolate")
        torque_y = torsion(spanwise_location)

        wingbox_points = database_connector.load_wingbox_value("wingbox_points")
        G = database_connector.load_wingbox_value("shear_modulus_pa")
        chord_length = aerodynamic_data.chord_function(spanwise_location)
        centroid = get_centroid(spanwise_location)

        distances_1 = (wingbox_points[0][0] - centroid[0], wingbox_points[0][1] - centroid[1])
        distances_2 = (wingbox_points[1][0] - centroid[0], wingbox_points[1][1] - centroid[1])
        distances_3 = (wingbox_points[2][0] - centroid[0], wingbox_points[2][1] - centroid[1])
        distances_4 = (wingbox_points[3][0] - centroid[0], wingbox_points[3][1] - centroid[1])
        distances_5 = (wingbox_points[4][0] - centroid[0], wingbox_points[4][1] - centroid[1])
        distances_6 = (wingbox_points[5][0] - centroid[0], wingbox_points[5][1] - centroid[1])

        length_12 = abs(distances_1[0] - distances_2[0]) * chord_length
        length_23 = abs(distances_2[0] - distances_3[0]) * chord_length
        length_34 = abs(distances_3[1] - distances_4[1]) * chord_length
        length_61 = abs(distances_6[1] - distances_1[1]) * chord_length
        length_25 = abs(distances_2[1] - distances_5[1]) * chord_length

        t_12 = t_23 = t_45 = t_56 = database_connector.load_wingbox_value("plate_thickness")
        t_34 = t_61 =  t_25 = database_connector.load_wingbox_value("spar_thickness")

        encl_area_1256 = (length_25 + length_61) * length_12 / 2
        encl_area_2345 = (length_25 + length_34) * length_23 / 2

        # Matrix
        matrix = np.array([[2 * encl_area_1256, 2 * encl_area_2345, 0],
                           [1 / (2 * encl_area_1256 * G) * (1 / t_12 + 1 / t_61 + 1 / t_25 + 1 / t_56),
                            1 / (2 * encl_area_1256 * G) * (- 1 / t_25), -1],
                           [1 / (2 * encl_area_2345 * G) * (- 1 / t_25),
                            1 / (2 * encl_area_2345 * G) * (1 / t_23 + 1 / t_34 + 1 / t_45 + 1 / t_25), -1]])

        # SHEAR DUE TO TORQUE
        solution_vector_t = np.array([torque_y, 0, 0])
        q_t_1256, q_t_2345, dtheta_t = np.linalg.solve(matrix, solution_vector_t)

        q_t = (q_t_1256 , q_t_2345)

    else:
        q_t_a = Torsion/2*Am
        q_t = (q_t_a , q_t_a)
        
    
    return q_t 

def get_tau_max(q_t , tau_avg, kv, t):

    tau_max_1 = kv* tau_avg + (q_t[0]/t)
    tau_max_2 = kv* tau_avg + (q_t[1]/t)
    tau_max = max(tau_max_1, tau_max_2)
    return tau_max 

    
def shear_stress_SPARS(b):
    list_coordinates = [(0.15, 0.06588533), (0.6, 0.0627513), (0.6, -0.02702924), (0.15, -0.04083288)]
    AC = AC_lenght(b)
    lenghts = get_lenghts(list_coordinates)
    slopes = get_slopes(list_coordinates)


    t_spar = 0.03 #MANUALLY TYPE IN
    kv = 1 #nsert #MANUALY TYPE IN

    tau_average = get_t_avg( t_spar , lenghts, z_shear(b), AC, get_centroid(b), list_coordinates, slopes , b)
    torque_shear = torque_shear_flow( AC, torsion(b),b,  list_coordinates)

    tau_max_SPAR = get_tau_max(torque_shear , tau_average, kv, t_spar)
    return tau_max_SPAR



def get_t_avg_skin(t, lenghts, x_shear, AC):


    h_top_skin = lenghts[0]*AC
    h_bottom_skin = lenghts[2]*AC

    tau_avg_skin = - x_shear/ (t* h_top_skin + t*h_bottom_skin)
    
    return tau_avg_skin

def shear_stress_SKIN(b):

    list_coordinates = [(0.15, 0.06588533), (0.6, 0.0627513), (0.6, -0.02702924), (0.15, -0.04083288)]
    AC = AC_lenght(b)
    lenghts = get_lenghts(list_coordinates)
    slopes = get_slopes(list_coordinates)

    t_skin = 0.045 #MANUALLY TYPE IN
    kv = 1 #TYPE IN
    
    tau_avg_skin = get_t_avg_skin(t_skin, lenghts, x_shear(b), AC)
    torque_shear = torque_shear_flow( AC, torsion(b), b, list_coordinates)
    tau_max_SKIN = get_tau_max(torque_shear , tau_avg_skin, kv, t_skin)
    return tau_max_SKIN


print(shear_stress_SPARS(10.1) , shear_stress_SKIN(10.1))

plt.suptitle("Moment of inertia")
plt.subplot(121)
plt.title("shear stress spar")
plt.ylabel("shear stress spar")
plt.xlabel("Spanwise location on a wing (m)")
plt.ylim(-100000000, 1000000000)
yy = []
xx = []
span = np.arange(0, 26.7890672, 0.01)

for i in span:
    value = shear_stress_SPARS(i)
    xx.append(value)

    #yy.append(value[1])
for i in span:
    value = shear_stress_SKIN(i)
    yy.append(value)

plt.plot(span, xx)
plt.subplot(122)
plt.title("shear stress skin")
plt.ylabel("Moment of inertia (m^4)")
plt.xlabel("Spanwise location on a wing (m)")
plt.ylim(-100000000, 10000000)
plt.plot(span, yy)
plt.show()



    


#list_coordinates = [(0.15, 0.06588533), (0.6, 0.0627513), (0.6, -0.02702924), (0.15, -0.04083288)]

#skin 