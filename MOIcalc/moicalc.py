import json
from matplotlib import pyplot as plt
import numpy as np
import math

try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()


# COORDINATES:___________________________________________________
# list_coordinates = [(0.15, 0.0627513), (0.6, 0.0627513), (0.6, -0.02702924), (0.15, -0.04083288)]


# Class of Parts:
# ____________________________________________

class Part:
    def __init__(self, lenght, thickness, area, angle):
        self.LEN = lenght
        self.T = thickness
        self.AREA = area
        self.ANGL = angle


# Dummy values
F_SP = 0
B_SP = 0
T_PL = 0
B_PL = 0
M_SP = 0


# ____________________________________________

# FUNCTIONS

# -------------------------------------------------------
# WING
# -------------------------------------------------------

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


# --------------------------------------------------------
# WING BOX
# --------------------------------------------------------

def len_t_angl_area(AC, t1, t2, t3, t4, t5):
    list_LEN = []
    list_T = []
    list_AREA = []
    list_ANGL = []

    # COORDINATES:___________________________________________________
    list_coordinates = [(0.15, 0.0627513), (0.6, 0.0627513), (0.6, -0.02702924), (0.15, -0.04083288)]
    x1 = list_coordinates[0][0]
    y1 = list_coordinates[0][1]

    x2 = list_coordinates[1][0]
    y2 = list_coordinates[1][1]

    x3 = list_coordinates[2][0]
    y3 = list_coordinates[2][1]

    x4 = list_coordinates[3][0]
    y4 = list_coordinates[3][1]

    # LENGHTS, THICKNESS, AREA, SLOPES, ANGLES:______________________________

    # Front spar (0.15*AC)

    F_SP_LEN = abs((y1 - y4)) * AC
    F_SP_T = t1
    F_SP_AREA = F_SP_LEN * F_SP_T
    F_SP_ANGL = 0

    list_LEN.append(F_SP_LEN)
    list_T.append(F_SP_T)
    list_AREA.append(F_SP_AREA)
    list_ANGL.append(F_SP_ANGL)

    # Back spar (0.6*AC)

    B_SP_LEN = abs((y2 - y3)) * AC
    B_SP_T = t2
    B_SP_AREA = B_SP_LEN * B_SP_T
    B_SP_ANGL = 0

    list_LEN.append(B_SP_LEN)
    list_T.append(B_SP_T)
    list_AREA.append(B_SP_AREA)
    list_ANGL.append(B_SP_ANGL)

    # Top plate

    T_PL_LEN = (math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)) * AC
    T_PL_T = t3
    T_PL_AREA = T_PL_LEN * T_PL_T
    T_PL_SL = (y2 - y1) / (x2 - x1)
    T_PL_ANGL = math.atan(T_PL_SL)

    list_LEN.append(T_PL_LEN)
    list_T.append(T_PL_T)
    list_AREA.append(T_PL_AREA)
    list_ANGL.append(T_PL_ANGL)

    # Bottom plate

    B_PL_LEN = (math.sqrt((x3 - x4) ** 2 + (y3 - y4) ** 2)) * AC
    B_PL_T = t4
    B_PL_AREA = B_PL_LEN * B_PL_T
    B_PL_SL = (y3 - y4) / (x3 - x4)
    B_PL_ANGL = math.atan(B_PL_SL)

    list_LEN.append(B_PL_LEN)
    list_T.append(B_PL_T)
    list_AREA.append(B_PL_AREA)
    list_ANGL.append(B_PL_ANGL)

    # Middle spar:

    M_SP_T = t5
    M_SP_ANGL = 0
    list_T.append(M_SP_T)
    list_ANGL.append(M_SP_ANGL)

    # _____
    out = []
    out.append(list_LEN)
    out.append(list_T)
    out.append(list_AREA)
    out.append(list_ANGL)

    return out


# --------------------------------------------------------
# CENTROID
def centroids_of_shapes(AC, F_SP, B_SP, T_PL, B_PL, M_SP):
    # COORDINATES:___________________________________________________
    list_coordinates = [(0.15, 0.0627513), (0.6, 0.0627513), (0.6, -0.02702924), (0.15, -0.04083288)]
    x1 = list_coordinates[0][0]
    y1 = list_coordinates[0][1]

    x2 = list_coordinates[1][0]
    y2 = list_coordinates[1][1]

    x3 = list_coordinates[2][0]
    y3 = list_coordinates[2][1]

    x4 = list_coordinates[3][0]
    y4 = list_coordinates[3][1]

    # Centroids of each shape (with respect to unit chord):

    list_x = []
    list_y = []
    lists_x_y = []

    # ___

    F_SP_CNTRY = ((F_SP.LEN / 2) + y4 * AC) / AC
    F_SP_CNTRX = 0.15

    list_x.append(F_SP_CNTRX)
    list_y.append(F_SP_CNTRY)

    # ___

    B_SP_CNTRY = ((F_SP.LEN / 2) + y3 * AC) / AC
    B_SP_CNTRX = 0.6

    list_x.append(B_SP_CNTRX)
    list_y.append(B_SP_CNTRY)

    # ___

    T_PL_CNTRY = y2
    T_PL_CNTRX = ((T_PL.LEN / 2) + 0.15 * AC) / AC

    list_x.append(T_PL_CNTRX)
    list_y.append(T_PL_CNTRY)

    # ___

    B_PL_CNTRY = (y3 * AC - ((B_PL.LEN / 2) * math.sin(B_PL.ANGL))) / AC
    B_PL_CNTRX = ((B_PL.LEN / 2) * math.cos(B_PL.ANGL) + 0.15 * AC) / AC

    list_x.append(B_PL_CNTRX)
    list_y.append(B_PL_CNTRY)

    # ___

    lists_x_y.append(list_x)
    lists_x_y.append(list_y)

    return lists_x_y


def spar_cntr_dist_TBPL(centroid, AC):  # FOR CALRO PART (return: values = [ , , , ,])
    # COORDINATES:___________________________________________________
    list_coordinates = [(0.15, 0.0627513), (0.6, 0.0627513), (0.6, -0.02702924), (0.15, -0.04083288)]
    x1 = list_coordinates[0][0]
    y1 = list_coordinates[0][1]
    x2 = list_coordinates[1][0]
    y2 = list_coordinates[1][1]
    x3 = list_coordinates[2][0]
    y3 = list_coordinates[2][1]
    x4 = list_coordinates[3][0]
    y4 = list_coordinates[3][1]

    values = []

    fS_centroidtoTOP = abs(centroid[1] - y1) * AC
    fS_centroidtoBOT = abs(centroid[1] - y4) * AC  # Front SPAR Distance Centroid to BOT
    rS_centroidtoTOP = abs(centroid[1] - y2) * AC  # Rear SPAR Distance Centroid to TOP
    rS_centroidtoBOT = abs(centroid[1] - y3) * AC  # Rear SPAR Distance Centroid to BOT
    interspar_spacing = (x2 - x1) * AC  # horizontal distance between front and rear spars
    fS_centroidtofs = abs(centroid[0] - x1) * AC  # x distance from centroid to F_SP
    rs_centroidtors = abs(centroid[0] - x2) * AC  # x distance from centroid to R_SP

    values.append(fS_centroidtoTOP)
    values.append(fS_centroidtoBOT)
    values.append(rS_centroidtoTOP)
    values.append(rS_centroidtoBOT)

    values.append(interspar_spacing)  # 4
    values.append(fS_centroidtofs)  # 5
    values.append(rs_centroidtors)  # 6

    return values


# Main centroid:

def centroid_nomspar(lists_x_y, F_SP, B_SP, T_PL, B_PL, M_SP):
    listxy = lists_x_y
    list_AREA = [F_SP.AREA, B_SP.AREA, T_PL.AREA, B_PL.AREA]
    list_x = listxy[0]
    list_y = listxy[1]
    SUM_AREA = sum(list_AREA)

    LIST_X_AC = [element * 1 for element in list_x]
    SUM_XA = sum([a * b for a, b in zip(LIST_X_AC, list_AREA)])

    LIST_Y_AC = [element * 1 for element in list_y]
    SUM_YA = sum([a * b for a, b in zip(LIST_Y_AC, list_AREA)])

    X = SUM_XA / SUM_AREA
    Y = SUM_YA / SUM_AREA

    wingbox_centroid_location_nomspar = [X, Y]

    return wingbox_centroid_location_nomspar


def mspar(list, AC, F_SP, B_SP, T_PL, B_PL, M_SP):  # with respect to AC

    # COORDINATES:___________________________________________________
    list_coordinates = [(0.15, 0.0627513), (0.6, 0.0627513), (0.6, -0.02702924), (0.15, -0.04083288)]
    x1 = list_coordinates[0][0]
    y1 = list_coordinates[0][1]

    x2 = list_coordinates[1][0]
    y2 = list_coordinates[1][1]

    x3 = list_coordinates[2][0]
    y3 = list_coordinates[2][1]

    x4 = list_coordinates[3][0]
    y4 = list_coordinates[3][1]

    x = list[0]
    y = list[1]

    M_SP_LEN = (F_SP.LEN - (F_SP.LEN - B_SP.LEN) + ((x2 - x) * math.tan(B_PL.ANGL) * AC))
    M_SP_CNTRY = ((M_SP_LEN / 2) / AC) - (-y3 + ((x2 - x) * math.tan(B_PL.ANGL)))
    M_SP_CNTRX = list[0]
    M_SP_AREA = M_SP.T * M_SP_LEN
    M_SP_centroid_A = []
    M_SP_centroid_A.append(M_SP_CNTRX)
    M_SP_centroid_A.append(M_SP_CNTRY)
    M_SP_centroid_A.append(M_SP_AREA)
    M_SP_centroid_A.append(M_SP_LEN)

    return M_SP_centroid_A


def centroid_w_mspar(M_SPcentroid, lists_x_y, F_SP, B_SP, T_PL, B_PL, M_SP):
    list_AREA = [F_SP.AREA, B_SP.AREA, T_PL.AREA, B_PL.AREA]
    list_AREA.append(M_SPcentroid[2])
    list_x = lists_x_y[0]
    list_y = lists_x_y[1]
    list_x.append(M_SPcentroid[0])
    list_y.append(M_SPcentroid[1])

    SUM_AREA = sum(list_AREA)

    SUM_XA = sum([a * b for a, b in zip(list_x, list_AREA)])

    SUM_YA = sum([a * b for a, b in zip(list_y, list_AREA)])

    X = SUM_XA / SUM_AREA
    Y = SUM_YA / SUM_AREA

    wingbox_centroid_location_wmspar = [X, Y]
    return wingbox_centroid_location_wmspar


# ---------------------------------------------------------
# MOI CALCULATIONS: 

def moi(centroid, centroids, M_SPcentroid, F_SP, B_SP, T_PL, B_PL, M_SP, b):  # Alvaro

    t1 = F_SP.T
    t3 = B_SP.T
    t2 = T_PL.T
    t4 = B_PL.T
    t5 = M_SP.T

    # length
    l1 = F_SP.LEN
    l3 = B_SP.LEN
    l2 = T_PL.LEN
    l4 = B_PL.LEN
    l5 = M_SP.LEN

    # slope
    B = B_PL.ANGL
    # area?
    # centroid = [X,Y], centroids [[all x],[all y]]
    # centroid:
    X = centroid[0]
    Y = centroid[1]

    x1 = abs(X - centroids[0][0])
    y1 = abs(Y - centroids[1][0])

    x2 = abs(X - centroids[0][2])
    y2 = abs(Y - centroids[1][2])

    x3 = abs(X - centroids[0][1])
    y3 = abs(Y - centroids[1][1])

    x4 = abs(X - centroids[0][3])
    y4 = abs(Y - centroids[1][3])

    x5 = abs(X - M_SPcentroid[0])
    y5 = abs(X - M_SPcentroid[1])

    # CODE 1 to calculate Ixx

    # For front  spar
    Ixx1 = (t1 * l1 ** 3) / 12
    xST1 = t1 * l1 * y1 ** 2

    # top plate
    Ixx2 = 0  # (l2 * t2**3)/12   thin wall assumption, ignore this term
    xST2 = t2 * l2 * y2 ** 2

    # back spar
    Ixx3 = (t3 * l3 ** 3) / 12
    xST3 = t3 * l3 * y3 ** 2

    # bottom plate
    Ixx4 = (l4 ** 3 * t4 * (math.sin(B) ** 2)) / 12
    xST4 = t4 * l4 * y4 ** 2

    # medium spar
    Ixx5 = (t5 * l5 ** 3) / 12
    xST5 = 0
    # print(Ixx1)                #Just used to try effectiveness of code, can be removed when necessary

    # CODE 2 to calculate Iyy

    # For front  spar
    Iyy1 = 0  # Thin wall assumption (l1 * t1**3)/12
    yST1 = t1 * l1 * x1 ** 2

    # top plate
    Iyy2 = (t2 * l2 ** 3) / 12
    yST2 = t2 * l2 * x2 ** 2

    # back spar
    Iyy3 = 0  # (l_3 * t_3**3)/12 thin wall assumption
    yST3 = t3 * l3 * x3 ** 2

    # bottom plate
    Iyy4 = (l4 ** 3 * t4 * (math.cos(B) ** 2)) / 12
    yST4 = t4 * l4 * x4 ** 2

    # medium spar
    Iyy5 = 0  # (l_5 * t_5**3)/12 thin wall assumption
    yST5 = 0  # Just used to try effectiveness of code, can be removed when necessary

    if b <= 10:

        # final Iyy ans
        Iyy = Iyy1 + Iyy2 + Iyy3 + Iyy4 + Iyy5 + yST1 + yST2 + yST3 + yST4 + yST5

        # final Ixx ans
        Ixx = Ixx1 + Ixx2 + Ixx3 + Ixx4 + Ixx5 + xST1 + xST2 + xST3 + xST4 + xST5  # !!!!!!!!!!!!!!!!!
    else:
        Iyy = Iyy1 + Iyy2 + Iyy3 + Iyy4 + yST1 + yST2 + yST3 + yST4

        # final Ixx ans
        Ixx = Ixx1 + Ixx2 + Ixx3 + Ixx4 + xST1 + xST2 + xST3 + xST4  # !!!!!!!!!!!!!!!!!

    MOI = [Ixx, Iyy]

    return MOI


def moi_stringers(b, values, stringer_amount, stringer_area):
    # START
    FS_centroidtoTOP = values[0]
    FS_centroidtoBOT = values[1]
    RS_centroidtoTOP = values[2]
    RS_centroidtoBOT = values[3]

    # float deltaH_top #Inner Stringer Vertical Height - Delta H TOP is deltaH_top
    # float deltaH_bot #Inner Stringer Vertical Height - Delta H BOT is deltaH_bot

    deltaH_top = (max(RS_centroidtoTOP, FS_centroidtoTOP) - min(RS_centroidtoTOP, FS_centroidtoTOP)) / (stringer_amount - 1)

    deltaH_bot = (max(RS_centroidtoBOT, FS_centroidtoBOT) - min(RS_centroidtoBOT, FS_centroidtoBOT)) / (stringer_amount - 1)

    MOI_String_TOP = 0

    for i in range(0, stringer_amount - 1):
        MOI_String_TOP = MOI_String_TOP + stringer_area * (min(RS_centroidtoTOP, FS_centroidtoTOP) + i * deltaH_top) ** 2

    MOI_String_BOT = 0

    for i in range(0, stringer_amount - 1):
        MOI_String_BOT = MOI_String_BOT + stringer_area * (min(RS_centroidtoBOT, FS_centroidtoBOT) + i * deltaH_bot) ** 2

    MOI_Xaxis = MOI_String_BOT + MOI_String_TOP

    engine_location = 10

    spar3rd = True

    if b > engine_location:
        spar3rd = False

    # 3rd SPAR condition
    if spar3rd == True:  # exist 3rd spar held by 2 stringers at centroid
        MOI_String_TOP = MOI_String_TOP + stringer_area * 2 * (min(RS_centroidtoTOP, FS_centroidtoTOP) + (stringer_amount - 1) / 2 * deltaH_top) ** 2
        MOI_String_BOT = MOI_String_BOT + stringer_area * 2 * (min(RS_centroidtoBOT, FS_centroidtoBOT) + (stringer_amount - 1) / 2 * deltaH_bot) ** 2
        MOI_Xaxis = MOI_String_BOT + MOI_String_TOP

    # VERTICAL STRINGERS********************************************************
    interspar_spacing = values[4]  # spacing between front spar and rear spar                   #!!!!!!!!!!!!!!!!
    # interstringer_spacing #spacing between 2 stringers                              X
    # re use stringer amount and area
    # assumption largest amoun of stringers goes to further side
    fS_centroidtofs = values[5]  # Distance Centroid wingbox to Front Spar                       #!!!!!!!!!!
    rs_centroidtors = values[6]  # Distance Centroid to Rear Spar                               # !!!!!!!!!!!

    #
    # #Calculate MOI points at centroid center third spar
    # float MS_centroidto TOP #distance centroid to top plate
    # float MS_centroidto BOT #distance centroid to bottom plate
    # float spar_to_spar_distance #distance between front and rear spar

    interstringer_spacing = interspar_spacing / (stringer_amount - 1)

    # Note that if springers are evenly spear out we get 2 x MOI
    # Assume equal amount of stringers in front and behind centroid
    # LEADING SIDE*******
    MOI_String_Left = 0
    for i in range(0, int((stringer_amount - 1) / 2) - 1):
        MOI_String_Left = MOI_String_Left + stringer_area * (fS_centroidtofs - i * interstringer_spacing) ** 2

    # TRAILING SIDE*******
    MOI_String_Right = 0
    for i in range(0, int((stringer_amount - 1) / 2) + 1):
        MOI_String_Right = MOI_String_Right + stringer_area * (rs_centroidtors - i * interstringer_spacing) ** 2

    # 3rd SPAR condition
    # When in first section where exist 3rd spar
    # Neglect increase in MOI z axis as located at cetroid so distance = 0

    MOI_Yaxis = MOI_String_Right + MOI_String_Left

    MOI_stringers = [MOI_Xaxis, MOI_Yaxis]

    return MOI_stringers


# ***********************************************
# MAIN FUNCTION:
# ***********************************************

def main(b, t1, t2, t3, t4, t5, Ns, As):  # ns - number of stringers #area of stringers

    AC = AC_lenght(b)
    out = len_t_angl_area(AC, t1, t2, t3, t4, t5)

    F_SP = Part(out[0][0], out[1][0], out[2][0], out[3][0])
    B_SP = Part(out[0][1], out[1][1], out[2][1], out[3][1])
    T_PL = Part(out[0][2], out[1][2], out[2][2], out[3][2])
    B_PL = Part(out[0][3], out[1][3], out[2][3], out[3][3])
    M_SP = Part(0, out[1][4], 0, out[3][4])

    two_spar_centroids = centroids_of_shapes(AC, F_SP, B_SP, T_PL, B_PL, M_SP)

    two_spar_centroid_wingbox = centroid_nomspar(two_spar_centroids, F_SP, B_SP, T_PL, B_PL, M_SP)

    middle_spar = mspar(two_spar_centroid_wingbox, AC, F_SP, B_SP, T_PL, B_PL, M_SP)

    M_SP = Part(middle_spar[3], out[1][4], middle_spar[2], out[3][4])

    three_spar_centroid = centroid_w_mspar(middle_spar, two_spar_centroids, F_SP, B_SP, T_PL, B_PL, M_SP)

    if b <= 10:
        new_centroid = three_spar_centroid
    else:
        new_centroid = two_spar_centroid_wingbox

    moment_of_inertia1 = moi(new_centroid, two_spar_centroids, middle_spar, F_SP, B_SP, T_PL, B_PL, M_SP, b)

    values = spar_cntr_dist_TBPL(new_centroid, AC)

    moment_of_inertia2 = moi_stringers(b, values, Ns, As)

    moment_of_inertia = [a + b for a, b in zip(moment_of_inertia1, moment_of_inertia2)]

    return moment_of_inertia


# print(main(0, 0.01, 0.01, 0.01, 0.01, 0.01, 4 , 0.001))  # <------- for testing
# print(main(26, 0.01, 0.01, 0.01, 0.01, 0.01, 4, 0.001))

# ***********************************************
# PLOT
# ***********************************************
def __main_w_c(b):  # For plotting

    # t1, t2, t3, t4, t5 , Ns, As 

    t1 = 0.01
    t2 = 0.01
    t3 = 0.01
    t4 = 0.01
    t5 = 0.01
    Ns = 4
    As = 0.001

    AC = AC_lenght(b)
    out = len_t_angl_area(AC, t1, t2, t3, t4, t5)

    F_SP = Part(out[0][0], out[1][0], out[2][0], out[3][0])
    B_SP = Part(out[0][1], out[1][1], out[2][1], out[3][1])
    T_PL = Part(out[0][2], out[1][2], out[2][2], out[3][2])
    B_PL = Part(out[0][3], out[1][3], out[2][3], out[3][3])
    M_SP = Part(0, out[1][4], 0, out[3][4])

    two_spar_centroids = centroids_of_shapes(AC, F_SP, B_SP, T_PL, B_PL, M_SP)

    two_spar_centroid_wingbox = centroid_nomspar(two_spar_centroids, F_SP, B_SP, T_PL, B_PL, M_SP)

    middle_spar = mspar(two_spar_centroid_wingbox, AC, F_SP, B_SP, T_PL, B_PL, M_SP)

    M_SP = Part(middle_spar[3], out[1][4], middle_spar[2], out[3][4])

    three_spar_centroid = centroid_w_mspar(middle_spar, two_spar_centroids, F_SP, B_SP, T_PL, B_PL, M_SP)

    if b <= 10:
        new_centroid = three_spar_centroid
    else:
        new_centroid = two_spar_centroid_wingbox

    moment_of_inertia1 = moi(new_centroid, two_spar_centroids, middle_spar, F_SP, B_SP, T_PL, B_PL, M_SP, b)

    values = spar_cntr_dist_TBPL(new_centroid, AC)

    moment_of_inertia2 = moi_stringers(b, values, Ns, As)

    moment_of_inertia = [a + b for a, b in zip(moment_of_inertia1, moment_of_inertia2)]

    return moment_of_inertia


def __plot(__main_w_c):
    # plot moment of inertia:
    plt.suptitle("Moment of inertia")
    plt.subplot(121)
    plt.title("Ixx")
    plt.ylim(0, 0.006)
    yy = []
    xx = []
    span = np.arange(0, 26.7890672, 0.01)

    for i in span:
        value = __main_w_c(i)
        xx.append(value[0])
        yy.append(value[1])

    plt.plot(span, xx)
    plt.subplot(122)
    plt.title("Izz")
    plt.ylim(0, 0.2)
    plt.plot(span, yy)
    plt.show()
    return


# ***********************************************
# POLAR MOMENT OF INERTIA
# ***********************************************


# ***********************************************
# BENDING DEFLECTION 
# ***********************************************

# will depend mainly on constant values that we put inside the the moment of inertia functions
# E is a constant, therefore (-1/E) is a constant and goes in front of integral
# v(span) = (-1/E) *integal(0, 26.smth) integral (0 , span) (Mx/Ixx)dspan dspan

def ixx(span):
    # t1, t2, t3, t4, t5 , Ns, As

    t1 = 0.01
    t2 = 0.01
    t3 = 0.01
    t4 = 0.01
    t5 = 0.01
    Ns = 4
    As = 0.001

    AC = AC_lenght(b)
    out = len_t_angl_area(AC, t1, t2, t3, t4, t5)

    F_SP = Part(out[0][0], out[1][0], out[2][0], out[3][0])
    B_SP = Part(out[0][1], out[1][1], out[2][1], out[3][1])
    T_PL = Part(out[0][2], out[1][2], out[2][2], out[3][2])
    B_PL = Part(out[0][3], out[1][3], out[2][3], out[3][3])
    M_SP = Part(0, out[1][4], 0, out[3][4])

    two_spar_centroids = centroids_of_shapes(AC, F_SP, B_SP, T_PL, B_PL, M_SP)
    two_spar_centroid_wingbox = centroid_nomspar(two_spar_centroids, F_SP, B_SP, T_PL, B_PL, M_SP)
    middle_spar = mspar(two_spar_centroid_wingbox, AC, F_SP, B_SP, T_PL, B_PL, M_SP)
    M_SP = Part(middle_spar[3], out[1][4], middle_spar[2], out[3][4])
    three_spar_centroid = centroid_w_mspar(middle_spar, two_spar_centroids, F_SP, B_SP, T_PL, B_PL, M_SP)

    if b <= 10:
        new_centroid = three_spar_centroid
    else:
        new_centroid = two_spar_centroid_wingbox

    moment_of_inertia1 = moi(new_centroid, two_spar_centroids, middle_spar, F_SP, B_SP, T_PL, B_PL, M_SP, b)
    values = spar_cntr_dist_TBPL(new_centroid, AC)
    moment_of_inertia2 = moi_stringers(b, values, Ns, As)
    moment_of_inertia = [a + b for a, b in zip(moment_of_inertia1, moment_of_inertia2)]
    moixx = moment_of_inertia[0]

    return moixx
# function of Mx(span)

# whole function Mx(span)/Ixx(span)

# (-1/E)*(sp.integrate.quad(func, 0, y)) ? Also non linear functions 
# first interval is (0 to y) 
# second interval (0 to 26)
