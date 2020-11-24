import json
import math

try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector


database_connector = DatabaseConnector()



#1) Numbers of parts:
# number of spars (3 at the beginning, later 2)
# number of top stringers
# number of bottom stringers




#-----------------------------------------------------
# WING
#-----------------------------------------------------

# Wing properties: (from the sheet)

b     =  database_connector.load_value("wing_span") 
t_c   =  database_connector.load_value("thickness_to_chord_ratio")
lambd =  database_connector.load_value("taper_ratio")
Cr    =  database_connector.load_value("root_chord")
Ct    =  database_connector.load_value("tip_chord")

hb = b/2 #half span

b_needed = float(input("Location on the half span? >"))

#trapezoid wing -> 
 
tan_alpha_wing = (Cr-Ct)/(2*hb) #angle between b and side of a trapezoid
AC = Ct + (2* tan_alpha_wing * (hb-b_needed))



#--------------------------------------------------------
# WING BOX
#--------------------------------------------------------


#COORDINATES: 
list_coordinates = [(0.15, 0.06588533), (0.6, 0.0627513), (0.6, -0.02702924), (0.15, -0.04083288)]

difference = abs(list_coordinates[0][1]-list_coordinates[1][1])

print(difference)
if difference < 0.01:
    first_coordinate = list(list_coordinates[0]) 
    first_coordinate[1] = list_coordinates[1][1]
    first_coordinate = tuple(first_coordinate)
    list_coordinates[0] = first_coordinate

else : 
    pass 


x1 =list_coordinates[0][0]
y1 = list_coordinates[0][1]

x2 =list_coordinates[1][0]
y2 = list_coordinates[1][1]

x3 =list_coordinates[2][0]
y3 = list_coordinates[2][1]

x4 =list_coordinates[3][0]
y4 = list_coordinates[3][1]

#LENGHTS AND SLOPES:

#Front spar (0.15*AC)

F_SP_LEN = abs((y1-y4))*AC
F_SP_T   = float(input("F SP thickness in m >"))
unit = F_SP_LEN/AC

#Back spar (0.6*AC)

B_SP_LEN = abs((y2-y3))*AC
B_SP_T   = float(input("B SP thickness in m >"))

#Top plate

T_PL_LEN = (math.sqrt((x2-x1)**2 + (y2-y1)**2))*AC
T_PL_SL  = (y2-y1)/(x2-x1)
T_PL_T   = float(input("T PL thickness in m >"))
T_PL_ANGL = math.atan(T_PL_SL)


#Bottom plate

B_PL_LEN = (math.sqrt((x3-x4)**2 + (y3-y4)**2))*AC
B_PL_SL  = (y3-y4)/(x3-x4)
B_PL_T   = float(input("B PL thickness in m >"))
B_PL_ANGL = math.atan(B_PL_SL)


#---------
#CENTROID 

#Centroids of each shape (with respect to unit chord):
list_AREA = []
list_x = []
list_y = []

F_SP_CNTRY = ((F_SP_LEN / 2) + y4*AC)/AC
F_SP_CNTRX = 0.15
F_SP_AREA  = F_SP_LEN * F_SP_T 
list_x.append(F_SP_CNTRX)
list_y.append(F_SP_CNTRY)
list_AREA.append(F_SP_AREA)

 
B_SP_CNTRY =  ((F_SP_LEN / 2) + y3*AC) / AC
B_SP_CNTRX = 0.6
B_SP_AREA = B_SP_LEN * B_SP_T
list_x.append(B_SP_CNTRX)
list_y.append(B_SP_CNTRY)
list_AREA.append(B_SP_AREA) 

T_PL_CNTRY = ((T_PL_LEN/2)*math.sin(T_PL_ANGL)+ y1*AC)/AC
T_PL_CNTRX = ((T_PL_LEN/2)*math.cos(T_PL_ANGL) + 0.15*AC)/AC
T_PL_AREA  = T_PL_LEN * T_PL_T
list_x.append(T_PL_CNTRX)
list_y.append(T_PL_CNTRY)
list_AREA.append(T_PL_AREA)

B_PL_CNTRY = (y4*AC + (B_PL_LEN/2)*math.sin(B_PL_ANGL))/AC
B_PL_CNTRX = ((B_PL_LEN/2)*math.cos(B_PL_ANGL)+ 0.15*AC)/AC
B_PL_AREA  = B_PL_LEN * B_PL_T 
list_x.append(B_PL_CNTRX)
list_y.append(B_PL_CNTRY)
list_AREA.append(B_PL_AREA)

#Main centroid:
SUM_AREA = sum(list_AREA)

LIST_X_AC = [element * 1 for element in list_x]
SUM_XA = sum([a * b for a, b in zip(LIST_X_AC, list_AREA)])

LIST_Y_AC =  [element * 1 for element in list_y]
SUM_YA = sum([a * b for a, b in zip(LIST_Y_AC, list_AREA)])

X = SUM_XA/SUM_AREA
Y = SUM_YA/SUM_AREA

wingbox_centroid_location = (X,Y) 

print(wingbox_centroid_location)



# MOI CALCULATIONS: 
#Ixx
#Iyy
#Ixy