from math import *
import pickle
import scipy as sp
from scipy import integrate, interpolate

try:
    from Database.database_functions import DatabaseConnector
    from CentroidCalculator.centroid_calculator import get_centroid
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    from CentroidCalculator.centroid_calculator import get_centroid


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
x_shear_lst = data[3]
z_shear_lst = data[5]
torsion_lst = data[7]
step = y_span_lst[1] - y_span_lst[0]

x_shear = sp.interpolate.interp1d(y_span_lst, x_shear_lst, kind="cubic", fill_value="extrapolate")
z_shear = sp.interpolate.interp1d(y_span_lst, z_shear_lst, kind="cubic", fill_value="extrapolate")
torsion = sp.interpolate.interp1d(y_span_lst, torsion_lst, kind="cubic", fill_value="extrapolate")


#def x(centroid, coordinates)

#                        0                    1               2                   3   
list_coordinates = [(0.15, 0.06588533), (0.6, 0.0627513), (0.6, -0.02702924), (0.15, -0.04083288)]
#unit lenghts
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
    #  0Top plate , 1LE spar , 2bottom plate , 3front spar (not adjusted for ac)

#unit slopes

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

print(lenghts)
print(slopes)
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
def z(centroid, list_coordinates, topstr, botstr, lenghts, slopes, distance, AC):
    #centroid = [x,z]
    #xc = centroid[0]
    yc = centroid[1]
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

def x(centroid, list_coordinates, topstr, botstr, lenghts, slopes, distance, AC):
    xc = centroid[0]
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


def delta_q_and_qb(z, x, areas, b):
    #Ixx = B*z^2 # Izz = b*x^2
    z_pw2 = [i ** 2 for i in z]
    x_pw2 = [i ** 2 for i in x]
    Ixx= sum([a * b for a, b in zip(areas, z_pw2)])
    Izz= sum([a * b for a, b in zip(areas, x_pw2)])

    Bx = [a * b for a, b in zip(areas, x)]
    Bz = [a * b for a, b in zip(areas, z)]

    #Vx =  #drag and thrust 
   # Vz =  #lift                     qb + ( - qs0)  +  (+qt )

    delta_q_list = []

    for i in len(areas):
        eq_delta_q = - (Vx/Izz)*Bx[i] - (Vz/Ixx)*Bz[i]
        delta_q_list.append(eq_delta_q)

    qb_list = [0] # [ q12 , q23 , q34 , ..... last one being 0  ]

    qb = 0
    for i in delta_q_list:
        qb = qb + i
        qb_list.append(qb)

    return qb_list


def qso(list_coordinates, qb_list, ):
    #Vx 
    #Vz 

    #qs0 is assumed to be ccw at first 
    # ccw is taken as positive 
    # 2Am*qs0 postitive 







#print(area_append(0.002 , 0.001, 5, 5 ))





#centroid = [0.3721599432362377, 0.014923830822928986]
#print(z(centroid, list_coordinates, 5, 5, lenghts, slopes, distances(5,5,lenghts), 10.44 ))
#print(x(centroid, list_coordinates, 5, 5, lenghts, slopes, distances(5,5,lenghts), 10.44 ))
  



    







#def x(centroid, coordinates)
