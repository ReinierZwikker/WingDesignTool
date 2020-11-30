# from Database.database_functions import DatabaseConnector
import matplotlib.pyplot as plt
import numpy as np

try:
    from Database.database_functions import DatabaseConnector
    from Gust_Loading_calculations_moved import W_list, U_ref, WoS, U_ds, F_g, rho_0, V_S1, V_C_cruise_altitude, rho_altitude
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    from Gust_Loading_calculations_moved import W_list, U_ref, WoS, U_ds, F_g, rho_0, V_S1, V_C_cruise_altitude, rho_altitude

database_connector = DatabaseConnector()

h = 0.5 * database_connector.load_value("operating_altitude_m")  # database_connector.load_value("operating_altitude_m") #height in m


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
            p = p_0 * np.exp((-g_0 / (R * T)) * (h1 - h_0))
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


T, p, rho = ISA_T_P_d(h)

# constants
mlw = database_connector.load_value("mlw_n")
oew = database_connector.load_value("oew")
mtow = database_connector.load_value("mtow")
C_L_max_flapped = database_connector.load_value("cl_max_flapped")
C_L_max_clean = database_connector.load_value("cl_max_clean")
V_C_TRUE = V_C_cruise_altitude  # .load_value("cruise_mach") * np.sqrt(1.4 * 287 * T)
S = database_connector.load_value("surface_area")

rho_0 = 1.225  # sea
w = 0.75 * mtow  # weight
W = (w / 9.81) / 0.454  # weight in lb for n_max

# constraints
n_max = 2.1 + ((24000) / (W + 10000))  # max load factor
if n_max < 2.5:
    n_max = 2.5
elif n_max > 3.8:
    n_max = 3.8
else:
    n_max = n_max

V_S0 = (np.sqrt((2 * w) / (C_L_max_flapped * rho * S))) * np.sqrt(
    rho_altitude / rho_0)  # stall speed with flaps extended.(should always be accompanied by a specification of which configuration the flaps are in (e.g. landing, take-off, etc.) EAS.
V_S1 = (np.sqrt((2 * w) / (C_L_max_clean * rho * S))) * np.sqrt(rho_altitude / rho_0)  # stall speed with flaps retracted EAS.
V_A = V_S1 * (np.sqrt(n_max))  # manoeuvring speed
V_C = V_C_TRUE * np.sqrt(rho_altitude / rho_0)  # design cruising speed EAS
V_D = V_C / 0.85  # design dive speed
# V_F = #design flap speed
V_EAS_0A = np.arange(0, V_A, 0.1)
V_EAS_02 = np.arange(0, np.sqrt(2) * V_S0, 0.1)
V_EAS_0H = np.arange(0, V_S1, 0.1)

n_min = -1  # CS25
n_0A = np.power((V_EAS_0A / V_S1), 2)
n_02 = np.power((V_EAS_02 / V_S0), 2)
n_0H = -np.power((V_EAS_0H / V_S1), 2)

# plotting-code
# plot-settings
# plt.ylim(-3, 3)
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.spines['bottom'].set_position('zero')
y_ticks = np.arange(-3, 5, 0.5)
x_ticks = np.arange(0, 400, 20)
plt.xticks(x_ticks)
plt.yticks(y_ticks)
plt.xlabel('V_EAS')
plt.ylabel('n')

# for line 0 to A
plt.plot(V_EAS_0A, n_0A, 'c')
# for line 0 to n=2
plt.plot(V_EAS_02, n_02, 'c')
# for line 0 to H
plt.plot(V_EAS_0H, n_0H, 'c')

# for line A to D n_max
x1, y1 = [V_A, V_D], [n_max, n_max]
# for line H to F
x2, y2 = [V_S1, V_C], [n_min, n_min]
# for line D to V_D
x3, y3 = [V_D, V_D], [n_max, 0]
# for line F to V_D
x4, y4 = [V_C, V_D], [n_min, 0]
# for line of n=2
x5, y5 = [np.sqrt(2) * V_S0, np.sqrt(2) * V_S1], [2, 2]
# for line V_s1
x6, y6 = [V_S1, V_S1], [n_min, np.power((V_S1 / V_S1), 2)]
# for line V_A
x7, y7 = [V_A, V_A], [n_min, n_max]
# for line V_C
x8, y8 = [V_C, V_C], [n_min, n_max]
# for line V_D
x9, y9 = [V_D, V_D], [0, n_max]

# draw lines
plt.plot(x1, y1, 'c', x2, y2, 'c', x3, y3, 'c', x4, y4, 'c', x5, y5, 'c')

# vertical lines
plt.plot(x6, y6, '--', label='V_S1')
plt.plot(x7, y7, '--', label='V_A')
plt.plot(x8, y8, '--', label='V_C')
plt.plot(x9, y9, '--', label='V_D')
plt.legend(loc='upper left', frameon=False)

# print values
print("V_S0 =", V_S0)
print("V_S1 =", V_S1)
print("V_A =", V_A)
print("V_C =", V_C)
print("V_D =", V_D)

# GUST DIAGRAM PART

# this graph requires to manually insert the variables
h_plot = h  # to be changed for other graphs
H_plot = 21
W_plot = W_list[0] + 0.5 * database_connector.load_value("fuel_max")
WS_plot = WoS(W_plot, S)
ISA_values = ISA_T_P_d(h_plot)
Uref_plot = U_ref(H_plot)
Uds_plot = U_ds(Uref_plot, F_g, H_plot)
from Gust_Loading_calculations_moved import V_S1, V_C, Cl_alpha, Cl_alpha_0, dn_s, g_0, V_D, V_B, \
    mean_geometric_chord  # leave this here

VS1_plot = V_S1(W_plot, ISA_values[2], rho_0, S, C_L_max_clean)

VC_plot_max = int(V_C_cruise_altitude) * np.sqrt(rho_altitude / rho_0)  # EAS
a_VC = Cl_alpha(Cl_alpha_0, VC_plot_max, ISA_values[0])
dn_VC = (dn_s(H_plot, WS_plot, a_VC, ISA_values[2], VC_plot_max * np.sqrt(rho_0 / rho_altitude), H_plot / VC_plot_max / np.sqrt(rho_0 / rho_altitude), Uds_plot, g_0))

VD_plot_max = int(V_D(VC_plot_max))
a_VD = Cl_alpha(Cl_alpha_0, VD_plot_max, ISA_values[0])
dn_VD = (dn_s(H_plot, WS_plot, a_VD, ISA_values[2], VD_plot_max * np.sqrt(rho_0 / rho_altitude), H_plot / VD_plot_max / np.sqrt(rho_0 / rho_altitude), 0.5 * Uds_plot, g_0))

VB_plot_max = int(V_B(WS_plot, ISA_values[2], mean_geometric_chord, Cl_alpha_0, g_0, rho_0, Uref_plot, VC_plot_max,
                      VS1_plot)) * np.sqrt(rho_altitude / rho_0)
a_VB = Cl_alpha(Cl_alpha_0, VB_plot_max, ISA_values[0])
dn_VB = (dn_s(H_plot, WS_plot, a_VB, ISA_values[2], VB_plot_max * np.sqrt(rho_0 / rho_altitude), H_plot / VB_plot_max / np.sqrt(rho_0 / rho_altitude), Uds_plot, g_0))

# gust lines
plt.plot([0, VB_plot_max], [1, 1 + dn_VB], 0.6, color="r")  # x-coor,ycoor,width,color
plt.plot([0, VC_plot_max], [1, 1 + dn_VC], 0.6, color="r")  # x-coor,ycoor,width,color
plt.plot([0, VD_plot_max], [1, 1 + dn_VD], '--', color="r")  # x-coor,ycoor,width,color

# negative lines
plt.plot([0, VB_plot_max], [1, 1 - dn_VB], 0.6, color="r")  # x-coor,ycoor,width,color
plt.plot([0, VC_plot_max], [1, 1 - dn_VC], 0.6, color="r")  # x-coor,ycoor,width,color
plt.plot([0, VD_plot_max], [1, 1 - dn_VD], '--', color="r")  # x-coor,ycoor,width,color

# vertical lines
plt.plot([VB_plot_max, VB_plot_max], [2.5, -1], '--', color="b", label='V_B')
plt.legend(loc='upper left', frameon=False)

# stall_speed connecting lines
plt.plot([VC_plot_max, VD_plot_max], [1 + dn_VC, 1 + dn_VD], 0.6, color="r")
plt.plot([VC_plot_max, VD_plot_max], [1 - dn_VC, 1 - dn_VD], 0.6, color="r")
plt.plot([VD_plot_max, VD_plot_max], [1 + dn_VD, 1 - dn_VD], 0.6, color="r")

# y = 1 axis
plt.plot([0, 1.15 * VD_plot_max], [1, 1], '--', color="r")

plt.ylabel('load factor')  # label on x-axis
plt.xlabel('EAS')  # label on y-axis

# show plot
plt.show()
