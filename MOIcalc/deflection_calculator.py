import pickle
import matplotlib.pyplot as plt
import scipy as sp
from scipy import interpolate


try:
    from Database.database_functions import DatabaseConnector
    from Integrator import Integration
    from MOIcalc.moicalc import inertia
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    from Integrator import Integration
    from MOIcalc.moicalc import inertia


database_connector = DatabaseConnector()

wing_span = database_connector.load_value("wing_span") / 2
outer_diameter = database_connector.load_value("df,outer")
radius_fuselage = outer_diameter / 2

E_Modulus = 68.9E9
# function of Mx(span)

# whole function Mx(span)/Ixx(span)


# (-1/E)*(sp.integrate.quad(func, 0, y)) ? Also non linear functions
# first interval is (0 to y)
# second interval (0 to 26)

try:
    with open("../InertialLoadingCalculator/data.pickle", 'rb') as file:
        data = pickle.load(file)
except FileNotFoundError:
    with open("./data.pickle", 'rb') as file:
        data = pickle.load(file)

spanwise_locations_list = data[0]
x_moment_data = data[3]
x_moment_func = sp.interpolate.interp1d(spanwise_locations_list, x_moment_data, kind="cubic", fill_value="extrapolate")
global_step_length = spanwise_locations_list[1] - spanwise_locations_list[0]


def deflection_double_derivative(y):
    return x_moment_func(y) / (E_Modulus * inertia(y)[0])


deflection_derivative_integral = Integration(deflection_double_derivative, wing_span, radius_fuselage, flip_sign=True)
deflection_integral = Integration(deflection_derivative_integral.get_value, wing_span, radius_fuselage, flip_sign=True)

deflection_derivative_data = []
deflection_data = []
for spanwise_location in spanwise_locations_list:
    deflection_derivative_data.append(deflection_derivative_integral.integrate(spanwise_location, -global_step_length))
    deflection_data.append(deflection_integral.integrate(spanwise_location, -global_step_length, -global_step_length))


print(f"Deflection is {max(deflection_data)} meters, requirement is {wing_span*0.30} meters")
#plt.figure(figsize=(20, 5))
plt.axis('equal')
plt.minorticks_on()
plt.grid('minor')
plt.plot([spanwise_locations_list[0], spanwise_locations_list[-1]], [wing_span*0.30, wing_span*0.30], '--r')
plt.plot(spanwise_locations_list, deflection_data)
plt.title("Bending Deflection")
plt.ylabel("Vertical Deflection(m)")
plt.xlabel("Spanwise location on a wing(m)")
plt.xlim(0,27)
plt.show()


















