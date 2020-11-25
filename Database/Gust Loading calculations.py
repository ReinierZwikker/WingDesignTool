# ------------ Here we work on the gust loading diagram ------------

from math import pi, sin, cos, tan, e, sqrt, exp

# # Import Wos, CLalpha,rho, V
# # WoS is W/S (W over S)


# Physical constants
g_0 = 9.80665  # m/s^2
R = 287.0  # J/kgK
# Sea level values:
T_0 = 288.15  # K
p_0 = 101325.0  # Pa
rho_0 = 1.225  # Kg/m^# 3

# Airplane Data
try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()

MLW = DatabaseConnector('mtow')


# MLW, MTOW, MZFW, Zmo!!!!, CLalpha


# ISA Calculator
def ISA_T_P_d(h, T_data, g_data, p_data):
    end = False
    T_0 = T_data
    g_0 = g_data
    p_0 = p_data
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

def WoS(W, S): # Wing loading
    return W / S


def V_B(WoS, rho, c, CLalpha, g, rho_0, Uref, V_C, Vs1):    # design speed for maximum gust intensity
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


def dn_s(H, WoS, CLalpha, rho, V, t, U_ds, g):      # load factor
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


# Body


# # iteration involves flight velocity, altitude, weight and gust gradient distance
# U_ds = U_ds(U_ref(H), F_g(MLW, MTOW, MZFW, Zmo), H)  # function of gust gradient distance
#
# Delta_n = dn_s(H, WoS, CLalpha, rho, V, t, U_ds, g_0)  # find which V goes there  thus what t

#
#
# def CLaM(CLa0, M):
#     # Cl alpha at cruise Mach
#     # M = cruise Mach
#     # CLa0 = CLa at M=0
#     CLaM = CLa0 / (math.sqrt(1 - M ** 2))
#     return CLaM
#
#
#
# # if __name__ == '__main__':
# #    main()
#
# g = 9.80665
# rho_0 = 1.225
# MLW =  # MZFW - reserve fuel !!!! this i could not find yet

#
# # load factor
#
# R1 = R1(MLW, MTOW)
#
# # import MZFW
# R2 = R2(MZFW, MTOW)
#
# F_gm = F_gm(R2, R1)
#
# # import Zmo from ____
# F_gz = F_gz(Zmo)
#
# F_g = F_g(F_gz, F_gm)
#
# Uref = Uref(h)
#
# # import Uref, H
# U_ds = U_ds(Uref, F_g, H)
#
# # t =
#
#
# # import WoS, CLalpha, rho, V
# la = la(WoS, CLalpha, rho, V, g)
#
# w = w(V, H)
#
# dn_s = dn_s(w, la, t, U_ds, g)
#
# # V_B
# # import WoS, rho, c, CLalpha, Uref, V_C, Vs1
#
# mu = mu(WoS, rho, c, CLalpha, g)
#
# K_g = K_g(mu)
#
# V_B = V_B(K_g, rho_0, Uref, V_C, CLalpha, WoS, Vs1)

print(MLW)