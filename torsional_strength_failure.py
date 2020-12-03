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

#constants
hb = database_connector.load_value("halfspan")

#normal stress stringers due to bending
def string_stress_normal(x, y, bl):
    M_y =
    M_x =
    I_yy =
    I_xx =
    I_xy =
    #b = #span location
    # x = #max distance to centroid
    # y = #max distance to centroid
    sigma = ((((M_x*I_yy)-(M_y*I_xy))*y)+(((M_y*I_xx)-(M_x*I_xy))*x))/((I_xx*I_yy)-(I_xy)**2)
    return sigma

def margin_of_safety(applied_stress):
    failure_stress = 310000000 #failurestress al6061-t6 in Pa(N/m**2)
    mos = failure_stress/applied_stress
    return mos

mos = margin_of_safety(5000)

#plotting-code
#plot-settings
#plt.ylim(-3, 3)
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.spines['bottom'].set_position('zero')
y_ticks = np.arange(-3, 5, 0.5)
x_ticks = np.arange(0, b/2, 0.5)
plt.xticks(x_ticks)
plt.yticks(y_ticks)
plt.xlabel('span')
plt.ylabel('margin of safety')

#for line 0 to A
plt.plot(bl, mos, 'c')

#show plot
plt.show()