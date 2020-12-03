from math import *
import matplotlib.pyplot as plt
import numpy as np

try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()

I = 0 # Moment of inertia per stringer
E = database_connector.load_wingbox_value("youngs_modulus_pa")
K = 4 #May vary per section in the wingbox. Needs to be determined manually per section.


def crit_stress_stringer(L): #L is the wingbox section length, thus rib spacing
    sigma = (K * (pi ** 2) * E * I) / (L**2)
    return sigma

try:
    from Integrator import Integration
    #from InertialLoadingCalculator.inertial_loading_calculator import ...
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    #from InertialLoadingCalculator.inertial_loading_calculator import ...
    from Database.database_functions import DatabaseConnector
    from Integrator import Integration

database_connector = DatabaseConnector()

#constants
hb = database_connector.load_value("wing_span")/2
length_steps = 0.5
i = 0 #location bl

#lists
bl_list = []
string_stress_nomral_list = []
mos_list = []

#normal stress stringers due to bending
def string_stress_normal(bl):
    M_y = 5*(60-bl)
    M_x = 4*(60-bl)
    I_yy = 20
    I_xx = 30
    I_xy = 20
    x = 0 #not #max distance to centroid
    y = 3 #not #max distance to centroid
    sigma = ((((M_x*I_yy)-(M_y*I_xy))*y)+(((M_y*I_xx)-(M_x*I_xy))*x))/((I_xx*I_yy)-(I_xy)**2)
    return sigma

def margin_of_safety(applied_stress):
    failure_stress = 310000000 #failurestress al6061-t6 in Pa(N/m**2)
    mos = failure_stress/applied_stress
    return mos

while i <= hb:
    applied_stress = string_stress_normal(i)
    string_stress_nomral_list.append(applied_stress)
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

