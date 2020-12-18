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

#enclosed_area = 0.5 * abs(sum(x0 * y1 - x1 * y0 for ((x0, y0), (x1, y1)) in area_segments([x * aerodynamic_data.chord_function(
  #  spanwise_location) for x in list_coordinates])))


#def x(centroid, coordinates)

#                        0                    1               2                   3   
#list_coordinates = [(0.15, 0.06588533), (0.6, 0.0627513), (0.6, -0.02702924), (0.15, -0.04083288)]
#unit lenghts
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

#distance between stringers
def distances(topstr, botstr, lenghts):

    numbers = [topstr, botstr]

    disttop = (lenghts[0])/(numbers[0]-1)
    distbot = (lenghts[2])/(numbers[1]-1)

    distance = [] #top, bottom 
    distance.append(disttop)
    distance.append(distbot)

    return distance #top, bottom (not adjusted for AC)

#print(distances(5,5,lenghts, 10.44))
#four stringers always locked 

#def z
def z(get_centroid, list_coordinates, topstr, botstr, lenghts, slopes, distance, AC):
    #centroid = [x,z]
    #xc = centroid[0]
    yc = get_centroid[1]/AC
    z_list = []
    #bottom

    for i in range(botstr): #positive down
        zb = (yc + (-list_coordinates[2][1]) + ( sin(atan(slopes[2]))*lenghts[2])) * AC #adjusted for AC

        z_list.append(zb)

        lenghts[2] = lenghts[2] - distance[1]
    #top
    for i in range(topstr): #positive down, thus values are negative
        zt = (( list_coordinates[1][1]-  yc) + ( sin(atan(slopes[0]))*lenghts[0])) * AC *(-1) #adjusted for AC

        z_list.append(zt)

        lenghts[0] = lenghts[0] - distance[0]

    return z_list #works

def x(get_centroid, list_coordinates, topstr, botstr, lenghts, slopes, distance, AC):
    xc = get_centroid[0]/AC
    x_list = []
    c1 = list_coordinates[0][0] #0.15c
    c2 = list_coordinates[1][0] #0.6c

    #distances towards TE spar are positive   ---------> +



    for i in range(botstr):
        xb = (xc - c1 - cos(atan(slopes[2]))*(distance[1])* i )*AC*(-1)
        x_list.append(xb)

    for i in range(topstr):
        xt = ( c2 - xc - cos(atan(slopes[0]))*(distance[0])* i )*AC
        x_list.append(xt)

    return x_list

def area_append(A1 , A2, topstr, botstr): #A1 is corner tringer area #A2 is normal stringer area (do we need to wa)

    area_list = [] 

    area_list.append(A1)

    for i in range(botstr-2):
        area_list.append(A2)

    area_list.append(A1)
    area_list.append(A1)

    for i in range(topstr-2):
        area_list.append(A2)

    area_list.append(A1)
    return area_list


def delta_q_and_qb(z, x, areas, b, x_shear, z_shear):
    #Ixx = B*z^2 # Izz = b*x^2
    z_pw2 = [i ** 2 for i in z]
    x_pw2 = [i ** 2 for i in x]
    Ixx= sum([a * b for a, b in zip(areas, z_pw2)])
    Izz= sum([a * b for a, b in zip(areas, x_pw2)])

    Bx = [a * b for a, b in zip(areas, x)]
    Bz = [a * b for a, b in zip(areas, z)]

    Vx =   - x_shear
    Vz =  - z_shear  

    #print (Vx, Vz)            
    delta_q_list = []

    for i in range(len(areas)):
        eq_delta_q = - (Vx/Izz)*Bx[i] - (Vz/Ixx)*Bz[i]
        delta_q_list.append(eq_delta_q)

    qb_list = [] # [ q12 , q23 , q34 , ..... last one being 0  ]
    #print(delta_q_list)

    qb = 0
    for i in delta_q_list:
        qb = qb + i
        qb_list.append(qb)

    return qb_list


def qso(list_coordinates, qb_list, slope_list , centroid, AC, b , Am , x_shear , z_shear, lenghts, botstr):  #need shear Vx(b) and Vz(b) from other program

    #point A is where the sloped sides 0f tapezoid join
    #since lengths are involved, adjusting for ac is needed 

    point_a = [2.9853 , 0.04614] #unit chord
    
    #ccw positive

    Vx = - x_shear
    #              >  both act on centroid 
    Vz = - z_shear

    a = botstr - 1


    Mqrs =  lenghts[1]*AC * qb_list[a] * (point_a[0] - 0.6) #NEEEED TO MAKE A FORMULA

    # cloclwise, Vz should be negative, ccw, Vx should be positive
    q_so = (Vz*(point_a[0] - (centroid[0]/AC))*AC + Vx * (point_a[1]-(centroid[1]/AC))*AC + Mqrs ) / (Am*2)

    return q_so

def qt(Torsion, Am):
    T =Torsion #AC adjusted torque

    #Am AC adjusted
    q_t = T/2*Am
    return q_t

def shear_flow(qb , qt , qso):
    qb_qso = [x+qso for x in qb]

    q = [x+qt for x in qb_qso]
    return q


def main_shear_stress(b):
    #basics

    list_coordinates = [(0.15, 0.06588533), (0.6, 0.0627513), (0.6, -0.02702924), (0.15, -0.04083288)]
   
    AC      = AC_lenght(b)
    lenghts = get_lenghts(list_coordinates)
    slopes  = get_slopes(list_coordinates)
    Am = 0.5 * abs(sum(x0 * y1 - x1 * y0 for ((x0, y0), (x1, y1)) in area_segments([x * aerodynamic_data.chord_function(b) for x in list_coordinates])))


    #******************************************************

    topstr = 5 #number of top stringers 
    botstr = 5 #number of bottom stingers
    A1     = 0.001 #area of corner stringers
    A2     = 0.001 #area of normal stringers
    t_spar = 1
    t_skin = 1


    distances_btwn_stringers = distances(topstr, botstr, lenghts)

    z_list = z(get_centroid(b), list_coordinates, topstr, botstr, lenghts, slopes, distances_btwn_stringers, AC)
    x_list = x(get_centroid(b), list_coordinates, topstr, botstr, lenghts, slopes, distances_btwn_stringers, AC)

    area_list = area_append(A1 , A2, topstr, botstr)

   # print(area_list)
   # print(x_list)
   # print(z_list)

    #****** shear*****
    qb_list = delta_q_and_qb(z_list, x_list, area_list, b, x_shear(b), z_shear(b))
    #print(qb_list)
    q_so = qso(list_coordinates, qb_list, slopes , get_centroid(b), AC, b , Am , x_shear(b), z_shear(b),lenghts, botstr)
    #print(q_so)
    q_t = qt(torsion(b), Am)
    #print(q_t)
    q_list = shear_flow(qb_list , q_t , q_so)
    
    thicc_list = []
    for i in range(botstr-1):
        thicc_list.append(t_skin)
    thicc_list.append(t_spar)
    for i in range(topstr-1):
        thicc_list.append(t_skin)
    thicc_list.append(t_spar)

    #print(thicc_list)
    shear_stress = [i / j for i, j in zip(q_list, thicc_list)]

    #max values 
    # max bottom
    bottom_shear_list = []
    for i in range(botstr-1):
        a = shear_stress[i] 
        bottom_shear_list.append(a)
    # spars
    spar_shear_stress_list = [shear_stress[botstr-1], shear_stress[-1]]
    top_plate_list = shear_stress[botstr : -1]

    bottom_shear_list_abs =  [abs(x) for x in bottom_shear_list]
    spar_shear_stress_list_abs = [abs(x) for x in spar_shear_stress_list]
    top_plate_list_abs= [abs(x) for x in top_plate_list]



    max_tau_bottom_plate = max(bottom_shear_list_abs)
    max_tau_top_plate = max(top_plate_list_abs)
    max_tau_spars = max(spar_shear_stress_list_abs)

    max_list = [max_tau_bottom_plate , max_tau_top_plate, max_tau_spars] #<---------------------------
    #print(q_list)
    #shear_stress_max = max(shear_stress)


    return max_list #shear_stress #_max





print(main_shear_stress(10))
#print(main_shear_stress(26))




#print(area_append(0.002 , 0.001, 5, 5 ))





#centroid = [0.3721599432362377, 0.014923830822928986]
#print(z(centroid, list_coordinates, 5, 5, lenghts, slopes, distances(5,5,lenghts), 10.44 ))
#print(x(centroid, list_coordinates, 5, 5, lenghts, slopes, distances(5,5,lenghts), 10.44 ))
  



    







#def x(centroid, coordinates)
