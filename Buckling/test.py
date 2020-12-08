import matplotlib.pyplot as plt
import numpy as np

try:
    from Integrator import Integration
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    from Integrator import Integration

database_connector = DatabaseConnector()

try:
    with open("../InertialLoadingCalculator/data.pickle", 'rb') as file:
        data = pickle.load(file)
except FileNotFoundError:
    with open("./data.pickle", 'rb') as file:
        data = pickle.load(file)

y_lst = data[0]
x_moment_lst = data[3]
z_moment_lst = data[6]

x_moment = sp.interpolate.interp1d(y_lst, x_moment_lst, kind="cubic", fill_value="extrapolate")
z_moment = sp.interpolate.interp1d(y_lst, z_moment_lst, kind="cubic", fill_value="extrapolate")

def normal_stress_stringer(moment_lift, moment_drag, z_location, x_location):
    sigma_stringer = (moment_lift*z_location)/Ixx + (moment_drag*x_location)/Izz


#constants
hb = database_connector.load_value("wing_span")/2
length_steps = 0.5
i = 0 #location bl

#lists
bl_list = []
string_stress_normal_list = []
mos_list = []

#normal stress stringers due to bending
def string_stress_normal(bl):
    M_z = 0
    M_x = 0
    I_zz = database_connector.load_wingbox_value("")
    I_xx = database_connector.load_wingbox_value("")
    I_xz = 0
    x = 0 #max distance to centroid
    z = 0 #max distance to centroid
    sigma = ((((M_x*I_zz)-(M_z*I_xz))*z)+(((M_z*I_xx)-(M_x*I_xz))*x))/((I_xx*I_yy)-(I_xz)**2)
    return sigma

while i <= hb:
    applied_stress = string_stress_normal(i)
    string_stress_normal_list.append(applied_stress)
    mos = margin_of_safety(applied_stress)
    mos_list.append(mos)
    bl_list.append(i)
    i += length_steps

#plotting-code
#plot-settings
#plt.ylim(-3, 3)
fig = plt.figure()
y_ticks = np.arange(0, 5, 0.5)
x_ticks = np.arange(0, hb, 5)
plt.xticks(x_ticks)
plt.yticks(y_ticks)
plt.xlabel('span location')
plt.ylabel('margin of safety')

#for line 0 to A
plt.plot(bl_list, mos_list, 'c')

#show plot
plt.show()

