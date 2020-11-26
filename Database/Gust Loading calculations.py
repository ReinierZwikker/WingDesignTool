# ------------ Here we work on the gust loading diagram ------------

from math import pi, sin, cos, tan, e, sqrt, exp

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
Cl_alpha_0 = database_connector.load_value("cl-alpha_curve")
S = database_connector.load_value("surface_area")
C_L_max_flapped = database_connector.load_value("cl_max_flapped")
C_L_max_clean = database_connector.load_value("cl_max_clean")


def V_C(T):  # TAS cruise speed
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


def V_B(WoS, rho, c, CLalpha, g, rho_0, Uref, V_C, Vs1):  # design speed for maximum gust intensity
    mu = (2 * WoS) / (rho * c * CLalpha * g)
    K_g = (0.88 * mu) / (5.3 + mu)
    A = K_g * rho_0 * Uref * V_C * CLalpha
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

    # only valid if 0 < t < 2pi/w
    A = 1 + (w * la) ** (-2)
    B = (e ** (-t / la)) / la
    C = (cos(w * t)) / la
    D = w * sin(w * t)
    E = B - C - D
    F = 1 / A
    G = U_ds / (2 * g)
    dn_s = G * (D + (F * E))
    return dn_s


def Cl_alpha(Cl_alpha_0, V, T):
    # Cl alpha at cruise Mach
    # M = cruise Mach
    M = V / sqrt(1.4 * 287 * T)
    # CLa0 = CLa at M=0
    CLaM = Cl_alpha_0 / (sqrt(1 - M ** 2))
    return CLaM


def V_S0(W, rho, rho_0, S, C_L_max_flapped):  # stall speed with flaps extended, TAS
    return (sqrt((2 * W) / (C_L_max_flapped * rho_0 * S))) * sqrt(rho / rho_0) * sqrt(rho_0 / rho)


def V_S1(W, rho, rho_0, S, C_L_max_clean):  # stall speed with flaps retracted,TAS
    return (sqrt((2 * W) / (C_L_max_clean * rho_0 * S))) * sqrt(rho / rho_0) * sqrt(rho_0 / rho)


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
W_list = [OEW, MLW, MTOW]  # List of weights constituting limit conditions

# REAL PROGRAM (Iterator to find the max load at the maximum conditions)

# pre-iteration variable
F_g = F_g(MLW, MTOW, MZFW, Zmo)
# place holder
list_H_h_W_V_Deltan = [0, 0, 0, 0, 0]

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

for H in range(H_interval[0], H_interval[1] + 3, 5):  # gust gradient iterator
    U_ref = U_ref(H)
    U_ds = U_ds(U_ref, F_g, H)  # function of gust gradient distance
    for h in range(0, operating_altitude, 100):  # altitude iterator
        ISA_values = ISA_T_P_d(h)
        for W in W_list:  # weight iterator
            WoS = WoS(W, S)
            V_S1 = V_S1(W, ISA_values[2], rho_0, S, C_L_max_clean)
            V_C = V_C(ISA_values[0])
            print(V_C)
            V_list = [V_S0(W, ISA_values[2], rho_0, S, C_L_max_flapped), V_S1,
                      V_A(V_S1, n_limit_VA(MTOW)),
                      V_B(WoS, ISA_values[2], mean_geometric_chord, Cl_alpha_0, g_0, rho_0, U_ref, V_C, V_S1),
                      V_C, V_D(V_C)]
            for V in V_list:  # speed iterator
                Delta_n = dn_s(H, WoS, Cl_alpha(Cl_alpha_0, V, ISA_values[0]), ISA_values[2], V, H / V, U_ds, g_0)

                if Delta_n > list_H_h_W_V_Deltan[4]:
                    list_H_h_W_V_Deltan = [H, h, W, V, Delta_n]

print(list_H_h_W_V_Deltan)