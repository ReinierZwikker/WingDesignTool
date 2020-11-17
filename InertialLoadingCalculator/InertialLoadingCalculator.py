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
Outer_diameter = database_connector.load_value("df,outer")
radius_fuselage = Outer_diameter / 2
surface_area = database_connector.load_value("surface_area")

global_length_step = 0.1  # [m]

# Define the flight conditions
test_velocity = 10.0  # m/s
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
def final_force_distribution(y, length_step, density, velocity):
    return lift_distribution(y, density, velocity) - weight_wing / (wing_span / (2 * length_step)) - weight_fuel / (wing_span / (2 * length_step))


# TODO Check if these integrals work

# Integrate to shear function
def shear_force_function(y, length_step, density, velocity):
    distributed_shear_force = sp.integrate.quad(final_force_distribution, radius_fuselage, y, (length_step, density, velocity))[0]
    if y < spanwise_location_engine:
        return distributed_shear_force + weight_engine
    else:
        return distributed_shear_force


# Integrate to moment function
def moment_function(y, length_step, density, velocity):
    return sp.integrate.quad(shear_force_function, radius_fuselage, y, (length_step, density, velocity))[0]


shear_force_data = []
moment_data = []
start_time_1 = time.time()
for y in np.arange(radius_fuselage, wing_span / 2, global_length_step):
    print(f"{y:.2f} / {wing_span/2}:")
    start_time_2 = time.time()
    shear_force_data.append(shear_force_function(y, global_length_step, test_density, test_velocity))
    print(time.time() - start_time_2)
    start_time_3 = time.time()
    moment_data.append(moment_function(y, global_length_step, test_density, test_velocity))
    print(time.time() - start_time_2)
print(time.time() - start_time_1)
# TODO Very slow from engine spanwise position?

plt.subplot(121)
plt.plot(np.arange(wing_span / 2, radius_fuselage, -global_length_step), shear_force_data, label="Shear")
plt.ylabel("Shear force (N/m2)")
plt.xlabel("Wing location (m)")
plt.subplot(122)
plt.plot(np.arange(wing_span / 2, radius_fuselage, -global_length_step), moment_data, label="Moment")
plt.ylabel("Moment (N/m)")
plt.xlabel("Wing location (m)")
plt.show()
