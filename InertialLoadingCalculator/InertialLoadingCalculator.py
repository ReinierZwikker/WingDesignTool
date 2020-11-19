### ------ Workpackage 4.1: Inertial loading calculations ------ ###
import scipy as sp
import numpy as np
from scipy import integrate
import time
import matplotlib.pyplot as plt

try:
    import Importer.xflr5 as aerodynamic_data
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    import Importer.xflr5 as aerodynamic_data
    from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()

# Import basic geometry
wing_span = database_connector.load_value("wing_span")
outer_diameter = database_connector.load_value("df,outer")
radius_fuselage = outer_diameter / 2
surface_area = database_connector.load_value("surface_area")

global_length_step = 0.1  # [m]

# Define the flight conditions
test_velocity = 50.0  # m/s
test_density = 1.225  # kg/m^2

# Import weight and location of the engine
weight_engine = database_connector.load_value("engine_weight")
spanwise_location_engine = database_connector.load_value("engine_spanwise_location")

# Import the weight of the wing and fuel (Class II)
weight_wing = database_connector.load_value("wing_weight")
weight_fuel = database_connector.load_value("fuel_max")


# Define the lift distribution
def lift_distribution(y, density, velocity):
    return aerodynamic_data.lift_coef_function_10(y) * 0.5 * density * (velocity ** 2) * surface_area


# Calculate the final force distribution
def z_final_force_distribution(y, length_step, density, velocity):
    # return lift_distribution(y, density, velocity) - weight_wing / (wing_span / (2 * length_step)) - weight_fuel / (wing_span / (2 * length_step))
    return 1


def add_engine_component(func, y, moment_arm):
    # if y < spanwise_location_engine:
    #     return func + moment_arm * weight_engine
    # else:
    #     return func
    return 0


# Integrate to shear function using scipy
def x_shear_force_function_scipy(spanwise_location, length_step, density, velocity):
    return - sp.integrate.quad(z_final_force_distribution, spanwise_location, wing_span / 2, length_step, density, velocity)[0]


# Integrate to moment function using scipy
def x_moment_function_scipy(spanwise_location, length_step, density, velocity):
    return - sp.integrate.quad(x_shear_force_function_scipy, spanwise_location, wing_span / 2, length_step, density, velocity)[0]


def trapz_area(prev_value, current_value, length_step):
    return prev_value + 0.5 * (current_value - prev_value) * length_step


x_shear_force_function_LUT = {}
x_moment_function_LUT = {}


# Integrate using trapezoid rule
def x_shear_force_function_trapz(start, stop, length_step, density, velocity):
    integral_value = 0
    for spanwise_location in np.arange(start, stop, length_step):
        if spanwise_location in x_shear_force_function_LUT:
            integral_value += x_shear_force_function_LUT[spanwise_location]
        else:
            prev_value = z_final_force_distribution(spanwise_location - length_step, length_step, density, velocity)
            current_value = z_final_force_distribution(spanwise_location, length_step, density, velocity)
            value = trapz_area(prev_value, current_value, length_step)
            integral_value += value
            x_shear_force_function_LUT[spanwise_location] = value

    return integral_value


# Integrate using trapezoid rule
def x_moment_function_trapz(start, stop, length_step, density, velocity):
    integral_value = 0
    for spanwise_location in np.arange(start, stop, length_step):
        if spanwise_location in x_moment_function_LUT:
            integral_value += x_moment_function_LUT[spanwise_location]
        else:
            prev_value = x_shear_force_function_trapz(spanwise_location - length_step, stop, length_step, density, velocity)
            current_value = x_shear_force_function_trapz(spanwise_location, stop, length_step, density, velocity)
            value = trapz_area(prev_value, current_value, length_step)
            integral_value += value
            x_moment_function_LUT[spanwise_location] = value
    return integral_value


spanwise_locations_list = np.arange(radius_fuselage, wing_span / 2, global_length_step)

z_force_data = []
x_shear_force_data = []
x_moment_data = []
start_time_1 = time.time()
total_time_taken = 0
for spanwise_location in spanwise_locations_list:
    start_time_2 = time.time()
    z_force_data.append(z_final_force_distribution(spanwise_location, global_length_step, test_density, test_velocity))
    x_shear_force_data.append(add_engine_component(x_shear_force_function_scipy(spanwise_location, wing_span/2, global_length_step, test_density, test_velocity), spanwise_location, 1))
    x_shear_time = time.time() - start_time_2
    start_time_3 = time.time()
    x_moment_data.append(add_engine_component(x_moment_function_trapz(spanwise_location, wing_span/2, global_length_step, test_density, test_velocity), spanwise_location, -(spanwise_location_engine - spanwise_location)))
    x_moment_time = time.time() - start_time_3
    print(f"{spanwise_location:.2f} / {wing_span / 2:.2f}:")
    print(f"Shear: {x_shear_time*1000:.5f} ms, Moment: {x_moment_time*1000:.5f} ms\n")
    total_time_taken += x_shear_time + x_moment_time
print(f"total time: {(time.time() - start_time_1)/60:.3f} min")
print(f"shear LUT length: {len(x_shear_force_function_LUT)}, moment LUT length: {len(x_moment_function_LUT)}")
# TODO Very slow from engine spanwise position? Kinda fixed

plt.subplot(221)
plt.plot(spanwise_locations_list, z_force_data, label="Force")
plt.ylabel("Applied Force in z (N)")
plt.xlabel("Wing location (m)")
plt.subplot(223)
plt.plot(spanwise_locations_list, x_shear_force_data, label="Shear")
plt.ylabel("Shear force in x (N)")
plt.xlabel("Wing location (m)")
plt.subplot(224)
plt.plot(spanwise_locations_list, x_moment_data, label="Moment")
plt.ylabel("Moment in x (Nm)")
plt.xlabel("Wing location (m)")
plt.show()
