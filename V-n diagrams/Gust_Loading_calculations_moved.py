# ------------ Here we work on the gust loading diagram ------------

from math import pi, sin, cos, tan, e, sqrt, exp
import matplotlib.pyplot as plt

# Physical constants (these values are also present in the ISA calculator and the il Cl_alpha calculator)
g_0 = 9.80665  # m/s^2
R = 287.0  # J/kgK
# Sea level values:
T_0 = 288.15  # K
p_0 = 101325.0  # Pa
rho_0 = 1.225  # Kg/m^# 3

# Airplane Data from connector
try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    # from WingData.chord_function import chord_function

database_connector = DatabaseConnector()

MLW = database_connector.load_value("mlw_n")
MTOW = database_connector.load_value("mtow")
OEW = database_connector.load_value("oew")
MZFW = OEW + database_connector.load_value("payload_max_n")
Zmo = database_connector.load_value("max_ceiling_m")
operating_altitude = database_connector.load_value("operating_altitude_m")
Cl_alpha_0 = database_connector.load_value("cl-alpha_curve") * pi / 180  # Now in radians
S = database_connector.load_value("surface_area")
C_L_max_flapped = database_connector.load_value("cl_max_flapped")
C_L_max_clean = database_connector.load_value("cl_max_clean")
Lambda_025 = database_connector.load_value("quarter_chord_sweep")
A_ratio = database_connector.load_value("aspect_ratio")
taper_ratio = database_connector.load_value("taper_ratio")
Lambda_050 = (Lambda_025 - 4 / A_ratio * (0.25 * (1 - taper_ratio) / (1 + taper_ratio))) * pi / 180


def V_C(T):  # TAS cruise speed
    # the cruise speed at 35000 feet (operating altitude is
    return database_connector.load_value("cruise_mach") * sqrt(1.4 * 287 * T)


mean_geometric_chord = 0.5 * (database_connector.load_value("root_chord") +
                              database_connector.load_value("tip_chord"))


# ISA Calculator
def ISA_T_P_d(h):
    end = False

    # constants
    g_0 = 9.80665  # m/s^2
    R = 287.0  # J/kgK
    # Sea level values:
    T_0 = 288.15  # K
    p_0 = 101325.0  # Pa
    h_0 = 0

    atm_layers = [0.0, 11000.0, 20000.0, 32000.0, 47000.0, 51000.0, 71000.0, 86000.0]
    atm_layerx = 1
    lay_coeff = [0.0, -0.0065, 0.0, +0.0010, +0.0028, 0.0, -0.0028, -0.0020]  # K/m

    while not end:
        # Layer Calculation
        h1 = min(h, atm_layers[atm_layerx])  # altitude
        T = T_0 + lay_coeff[atm_layerx] * (h1 - h_0)  # temperature
        if lay_coeff[atm_layerx] == 0.0:  # pressure
            p = p_0 * exp((-g_0 / (R * T)) * (h1 - h_0))
        else:
            p = p_0 * (T / T_0) ** (-g_0 / (lay_coeff[atm_layerx] * R))
        rho = p / (R * T)  # density

        if h <= atm_layers[atm_layerx]:
            end = True
        else:
            T_0 = T
            p_0 = p
            h_0 = h1
            atm_layerx = 1 + atm_layerx

    return T, p, rho


# Definition of Functions

def WoS(W, S):  # Wing loading
    return W / S


def V_B(WoS, rho, c, CLalpha, g, rho_0, Uref, VC, Vs1):  # design speed for maximum gust intensity
    mu = (2 * WoS) / (rho * c * CLalpha * g)
    K_g = (0.88 * mu) / (5.3 + mu)
    A = K_g * rho_0 * Uref * VC * CLalpha
    B = 2 * WoS
    return Vs1 * sqrt(1 + (A / B))


def U_ds(U_ref, F_g, H):  # gust design velocity
    U_ds = U_ref * F_g * (H / 107) ** (1 / 6)
    return U_ds


def U_ref(h):  # gust reference velocity follows from CS25.341
    if 0 <= h <= 4572:
        v0 = 17.07
        v1 = 13.41
        h0 = 0
        h1 = 4572
        b = v0
        dv = v1 - v0
        dh = h1 - h0
        a = dv / dh
    elif 4572 < h <= 18288:
        v1 = 13.41
        v2 = 6.36
        h1 = 4572
        h2 = 18288
        dv = v2 - v1
        dh = h2 - h1
        a = dv / dh
        b = v2 - (a * h2)
    return (a * h) + b


def F_g(MLW, MTOW, MZFW, Zmo):  # flight profile alleviation factor from CS25.341
    R1 = MLW / MTOW  # maximum landing weight / maximum take off weight
    R2 = MZFW / MTOW  # maximum zero fuel weight / maximum take off weight
    F_gm = sqrt(R2 * tan((pi * R1) / 4))
    F_gz = 1 - (Zmo / 76200)  # Zmo = maximum operating altitude
    return 0.5 * (F_gz + F_gm)


def dn_s(H, WoS, CLalpha, rho, V, t, U_ds, g):  # load factor
    # pre-ds calculations
    w = pi * V / H  # radial frequency of the response (omega)
    la = (2 * WoS) / (CLalpha * rho * V * g)  # lambda

    # # only valid if 0 < t < 2pi/w
    # A = 1 + (w * la) ** (-2)
    # B = (e ** (-t / la)) / la
    # C = (cos(w * t)) / la
    # D = w * sin(w * t)
    # E = B - C - D
    # F = 1 / A
    # G = U_ds / (2 * g)
    # dn_s = G * (D + (F * E))

    dn_s = U_ds / (2 * g) * (w * sin(w * t) + 1 / (1 + (w * la) ** -2) * (1 / la * e ** (- t / la)
                                                                          - 1 / la * cos(w * t) - w * sin(w * t)))
    return dn_s


def Cl_alpha(Cl_alpha_0, V, T):
    # Cl alpha at cruise Mach Prandt-Gauler correction
    # # M = cruise Mach
    M = V / sqrt(1.4 * 287 * T)
    # print(M)
    # # CLa0 = CLa at M=0
    # CLaM = Cl_alpha_0 / (sqrt(1 - M ** 2))

    # Datcom Method
    beta = sqrt(1 - M ** 2)
    CLaM = 2 * pi * A_ratio / (2 + sqrt(4 + ((A_ratio * beta / 0.95) ** 2) * (1 + tan(Lambda_050) ** 2) / beta ** 2))

    return CLaM


def V_S0(W, rho, rho_0, S, C_L_max_flapped):  # stall speed with flaps extended, TAS
    return sqrt((2 * W) / (C_L_max_flapped * rho * S))


def V_S1(W, rho, rho_0, S, C_L_max_clean):  # stall speed with flaps retracted, TAS
    return sqrt((2 * W) / (C_L_max_clean * rho * S))


def V_A(V_S1, n_limit_VA):  # manoeuvring speed
    return V_S1 * (sqrt(n_limit_VA))


def n_limit_VA(MTOW):
    W = (MTOW / 9.81) / 0.454  # weight in lb for n_max
    n_max = 2.1 + ((24000) / (W + 10000))  # max load factor
    if n_max < 2.5:
        n_max = 2.5
    elif n_max > 3.8:
        n_max = 3.8
    else:
        n_max = n_max
    return n_max


def V_D(V_C):  # design dive speed
    return V_C / 0.85


# Iterations infos
H_interval = (9, max(107, 12.5 * mean_geometric_chord))
V_C_cruise_altitude = V_C(ISA_T_P_d(database_connector.load_value("operating_altitude_m"))[0])
W_list = [OEW, MLW, MTOW]  # List of weights constituting limit conditions7
rho_altitude = ISA_T_P_d(operating_altitude)[2]

# REAL PROGRAM (Iterator to find the max load at the maximum conditions)

# pre-iteration variable
F_g = F_g(MLW, MTOW, MZFW, Zmo)
# place holder
list_H_h_W_V_Deltan = [0, 0, 0, 0, 0]
lspc = []

# # finding the time that produces the highest Delta-n (found to be H/V or simply half a cycle)
# t_evaluation_list = [0, 0]
# for t in range(0, 20, 1):  # to find the time at which the dns is maximum for every combination of the other variables
#     H_mock = 9
#     V_mock = H_mock
#     dn_s_mock = dn_s(H_mock, WoS(MTOW, S), Cl_alpha(Cl_alpha_0, V_mock, 288.15),
#     1.225, V_mock, t/10, U_ds(U_ref(H_mock), F_g, H_mock), g_0)
#     if dn_s_mock > t_evaluation_list[1]:
#         t_evaluation_list = [t, dn_s_mock]


# iteration involves (in order) gust gradient distance, altitude, weight and flight velocity

for H in range(H_interval[0], H_interval[1] + 1, 1):  # gust gradient iterator
    Uref = U_ref(H)
    Uds = U_ds(Uref, F_g, H)  # function of gust gradient distance
    for h in range(0, operating_altitude, 50):  # altitude iterator
        ISA_values = ISA_T_P_d(h)
        for X in W_list:  # weight iterator
            WS = WoS(X, S)
            VS1 = V_S1(X, ISA_values[2], rho_0, S, C_L_max_clean)
            VC = V_C_cruise_altitude
            VD = V_D(VC)
            V_list = [V_S0(X, ISA_values[2], rho_0, S, C_L_max_flapped), VS1,
                      V_A(VS1, n_limit_VA(MTOW)),
                      V_B(WS, ISA_values[2], mean_geometric_chord, Cl_alpha_0, g_0, rho_0, Uref, VC, VS1),
                      VC, VD]
            for V in V_list:  # speed iterator
                if V == VD:
                    Uds = 0.5 * Uds
                a = Cl_alpha(Cl_alpha_0, V, ISA_values[0])
                Delta_n = dn_s(H, WS, a, ISA_values[2], V, H / V, Uds, g_0)

                if Delta_n > list_H_h_W_V_Deltan[4]:
                    list_H_h_W_V_Deltan = [H, h, X, V, Delta_n, V * sqrt(rho_altitude / rho_0)]
                    lspc = [H, WS, a, ISA_values[2], V, H / V, Uds, g_0, VD, VC]

print(list_H_h_W_V_Deltan)

# Plot the variation in dn with the different variables in first position of 3 lines x 3 columns
plt.suptitle("Variation of Load Factor with Different Variables")

plt.subplot(231)
plt.title('gust gradient')
x_lst = []
x = range(H_interval[0], H_interval[1] + 1, 1)
for element in x:
    Uref = U_ref(element)
    Uds = U_ds(Uref, F_g, element)  # function of gust gradient distance
    x_lst.append(dn_s(element, lspc[1], lspc[2], lspc[3], lspc[4], element / lspc[4], Uds, lspc[7]))

# extra lines
crit_gust_shit = x[x_lst.index(max(x_lst))]

plt.plot([crit_gust_shit, crit_gust_shit], [max(x_lst), - 0.2], '--', color="b")  # x-coor,ycoor,width,color


plt.plot(x, x_lst, 0.6, color="r")  # x-coor,ycoor,width,color
plt.xlabel('gust gradient [m]')  # label on x-axis
plt.ylabel('difference in load factor')  # label on y-axis

plt.subplot(232)
plt.title('altitude')
altitude_lst = []
altitude = range(1, operating_altitude, 10)
for element in altitude:
    ISA_values = ISA_T_P_d(element)
    altitude_lst.append(
        dn_s(lspc[0], lspc[1], Cl_alpha(Cl_alpha_0, lspc[4], ISA_values[0]), ISA_values[2], lspc[4], lspc[5], lspc[6],
             lspc[7]))
plt.plot(altitude, altitude_lst, 0.6, color="r")  # x-coor,ycoor,width,color
plt.xlabel('altitude [m]')  # label on x-axis
plt.ylabel('difference in load factor')  # label on y-axis

plt.subplot(233)
plt.title('weight')
weight_lst = []
weight = range(int(W_list[0]), int(W_list[2]), 100)
for element in weight:
    WS = WoS(element, S)
    weight_lst.append(dn_s(lspc[0], WS, lspc[2], lspc[3], lspc[4], lspc[5], lspc[6], lspc[7]))
plt.plot(weight, weight_lst, 0.6, color="r")  # x-coor,ycoor,width,color
plt.xlabel('weight [N]')  # label on x-axis
plt.ylabel('difference in load factor')  # label on y-axis

plt.subplot(234)
plt.title('speed')
speed_lst = []
speed = range(1, int(lspc[9]), 5)
for element in speed:
    speed_lst.append(
        dn_s(lspc[0], lspc[1], Cl_alpha(Cl_alpha_0, element, ISA_values[0]), lspc[3], element, lspc[0] / element,
             lspc[6], lspc[7]))
plt.plot(speed, speed_lst, 0.6, color="r")  # x-coor,ycoor,width,color
plt.plot([lspc[9], lspc[9]], [0, speed_lst[-1]], '--', label='V_C')
plt.xlabel('speed [m/s]')  # label on x-axis
plt.ylabel('difference in load factor')  # label on y-axis

plt.subplot(235)
plt.title('time')
time_lst = []
percentage_lst = []
lst_weirdos = []
time = range(0, int(2 * lspc[0] / lspc[4] * 1000), 1)
for element in time:
    bb = dn_s(lspc[0], lspc[1], lspc[2], lspc[3], lspc[4], element / 1000, lspc[6], lspc[7])
    time_lst.append(bb)
    percentage_lst.append(element / (2 * lspc[0] / lspc[4]) / 10)
    if bb < 0:
        lst_weirdos.append(percentage_lst[-1])

plt.plot([lst_weirdos[0], lst_weirdos[0]], [min(time_lst), max(time_lst)], '--', label='V_C')

# time at which the delta load maximum is reached
crit_time = percentage_lst[time_lst.index(max(time_lst))]
print('The critical time is ' + str(crit_time) + "% of the total period")

# vertical lines

plt.plot([0, 100], [0, 0], 0.4, color="b")
plt.plot([crit_time, crit_time], [max(time_lst), -0.25], '--', color="b")

plt.plot(percentage_lst, time_lst, 0.6, color="r")  # x-coor,ycoor,width,color
plt.xlabel('percentage of time spent in the gust [%]')  # label on x-axis
plt.ylabel('difference in load factor')  # label on y-axis

plt.subplot(236)
plt.title('Gust Diagram')

# this graph requires to manually insert the variables
h_plot = 0  # to be changed for other graphs
H_plot = 25
W_plot = W_list[0]
WS_plot = WoS(W_plot, S)
ISA_values = ISA_T_P_d(h_plot)
Uref_plot = U_ref(H_plot)
Uds_plot = U_ds(Uref_plot, F_g, H_plot)
VS1_plot = V_S1(W_plot, ISA_values[2], rho_0, S, C_L_max_clean)

VC_plot_max = int(V_C_cruise_altitude) * sqrt(rho_altitude / rho_0)  # EAS
a_VC = Cl_alpha(Cl_alpha_0, VC_plot_max, ISA_values[0])
dn_VC = (dn_s(H_plot, WS_plot, a_VC, ISA_values[2], VC_plot_max * sqrt(rho_0 / rho_altitude), H_plot / VC_plot_max / sqrt(rho_0 / rho_altitude), Uds_plot, g_0))

VD_plot_max = int(V_D(VC_plot_max))
a_VD = Cl_alpha(Cl_alpha_0, VD_plot_max, ISA_values[0])
dn_VD = (dn_s(H_plot, WS_plot, a_VD, ISA_values[2], VD_plot_max * sqrt(rho_0 / rho_altitude), H_plot / VD_plot_max / sqrt(rho_0 / rho_altitude), 0.5 * Uds_plot, g_0))

VB_plot_max = int(V_B(WS_plot, ISA_values[2], mean_geometric_chord, Cl_alpha(Cl_alpha_0, 75, ISA_values[0]), g_0, rho_0, Uref_plot, VC_plot_max,
                      VS1_plot))
a_VB = Cl_alpha(Cl_alpha_0, VB_plot_max, ISA_values[0])
dn_VB = (dn_s(H_plot, WS_plot, a_VB, ISA_values[2], VB_plot_max, H_plot / VB_plot_max, Uds_plot, g_0

# gust lines
plt.plot([0, VB_plot_max], [1, 1 + dn_VB], 0.6, color="r")  # x-coor,ycoor,width,color
plt.plot([0, VC_plot_max], [1, 1 + dn_VC], 0.6, color="r")  # x-coor,ycoor,width,color
plt.plot([0, VD_plot_max], [1, 1 + dn_VD], '--', color="r")  # x-coor,ycoor,width,color

# negative lines
plt.plot([0, VB_plot_max], [1, 1 - dn_VB], 0.6, color="r")  # x-coor,ycoor,width,color
plt.plot([0, VC_plot_max], [1, 1 - dn_VC], 0.6, color="r")  # x-coor,ycoor,width,color
plt.plot([0, VD_plot_max], [1, 1 - dn_VD], '--', color="r")  # x-coor,ycoor,width,color

# vertical lines
plt.plot([VB_plot_max, VB_plot_max], [1 - 0.75 * dn_VC, 1 + 0.75 * dn_VC], '--', color="b", label='V_B')

# connecting lines
plt.plot([VC_plot_max, VD_plot_max], [1 + dn_VC, 1 + dn_VD], 0.6, color="r")
plt.plot([VC_plot_max, VD_plot_max], [1 - dn_VC, 1 - dn_VD], 0.6, color="r")
plt.plot([VD_plot_max, VD_plot_max], [1 + dn_VD, 1 - dn_VD], 0.6, color="r")

plt.plot([VC_plot_max, VC_plot_max], [1 + dn_VC, 1 - dn_VC], '--', color="r")

# x lines
plt.plot([0, 1.15 * VD_plot_max], [1, 1], '--', color="r", label='V_B')
plt.plot([0, 1.15 * VD_plot_max], [0, 0], 0.6, color="b", label='V_B')

plt.ylabel('load factor')  # label on x-axis
plt.xlabel('EAS [m/s]')  # label on y-axis

plt.show()
