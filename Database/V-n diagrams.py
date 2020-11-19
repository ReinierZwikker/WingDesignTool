from Database.database_functions import DatabaseConnector
import matplotlib.pyplot as plt
import numpy as np

database_connector = DatabaseConnector()

#constants
mtow = database_connector.load_value("mtow")
C_L_max_flapped = 2.47 #database_connector.load_value("cl_max_flapped")
C_L_max_clean = 1.56 #database_connector.load_value("cl_max_clean")
S = database_connector.load_value("surface_area")
rho_0 = 1.225 #sea
rho = 0.38035 #cruise

V_C_TRUE = database_connector.load_value("cruise_speed") #TRUE cruise speed
W = mtow/9.81/0.454 #weight in lb for n_max
w = mtow
n_max = 2.1 + (24000)/(W + 10000) #max load factor

V_s0 = np.sqrt((2*w)/(C_L_max_flapped*rho_0*S)) #stall speed with flaps extended.(should always be accompanied by a specification of which configuration the flaps are in (e.g. landing, take-off, etc.).
V_s1 = np.sqrt((2*w)/(C_L_max_clean*rho_0*S)) #stall speed with flaps retracted.
V_A = np.sqrt((2*n_max*w)/(rho*C_L_max_flapped*S)) #manoeuvring speed
V_C = V_C_TRUE*np.sqrt(rho/rho_0) #design cruising speed
V_D = V_C/0.8 #design dive speed
V_F = 85 #not correct design flap speed
V_EAS_0A = np.arange(0, V_A)
V_EAS_02 = np.arange(0, np.sqrt(2)*V_s0)
V_EAS_0H = np.arange(0, V_s1)

n_min = -1 #CS25
n_0A = np.power((V_EAS_0A/V_s1), 2)
n_02 = np.power((V_EAS_02/V_s0), 2)
n_0H = -np.power((V_EAS_0H/V_s1), 2)

#plotting-code
#plot-settings
plt.ylim(-3, 3)
y_ticks = np.arange(-3, 3, 0.5)
x_ticks = np.arange(0, 250, 20)
plt.xticks(x_ticks)
plt.yticks(y_ticks)

#for line 0 to A
plt.plot(V_EAS_0A, n_0A)
#for line 0 to n=2
plt.plot(V_EAS_02, n_02)
#for line 0 to H
plt.plot(V_EAS_0H, n_0H)

#for line A to D n_max
x1, y1 = [V_A, V_D], [n_max, n_max]
#for line H to F
x2, y2 = [V_s1, V_C], [n_min, n_min]
#for line D to V_D
x3, y3 = [V_D, V_D], [n_max, 0]
#for line F to V_D
x4, y4 = [V_C, V_D], [n_min, 0]
#for line of n=2
x5, y5 = [np.sqrt(2)*V_s0, V_F], [2, 2]

plt.plot(x1, y1, x2, y2, x3, y3, x4, y4, x5, y5)
plt.show()

if n_min < -1.0:
    print("n_min not allowed")

if n_max < 2.5 or n_max > 3.8:
    print(n_max)
    print("n_max not allowed")







