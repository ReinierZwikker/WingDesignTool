### ------ Workpackage 4.1: Inertial loading calculations ------ ###
import numpy as np
import time
import matplotlib.pyplot as plt

try:
    from Integrator import Integration
    import Importer.xflr5 as aerodynamic_data
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    import Importer.xflr5 as aerodynamic_data
    from Database.database_functions import DatabaseConnector
    from Integrator import Integration

database_connector = DatabaseConnector()

# Import basic geometry
wing_span = database_connector.load_value("wing_span")
outer_diameter = database_connector.load_value("df,outer")
radius_fuselage = outer_diameter / 2
surface_area = database_connector.load_value("surface_area")
root_chord = database_connector.load_value("root_chord")
tip_chord = database_connector.load_value("tip_chord")
taper_ratio = database_connector.load_value("taper_ratio")
spanwise_location_engine = database_connector.load_value("engine_spanwise_location")

chord_at_engine_location = aerodynamic_data.chord_function(spanwise_location_engine)
radius_engine = database_connector.load_value("d_engine")/2

moment_arm_engine = (0.25 + 0.2) * aerodynamic_data.chord_function(spanwise_location_engine)
moment_arm_thrust = 1.5 * radius_engine

global_length_step = 1  # [m]
LUT_rounding = 10  # digits

# Define the flight conditions
test_velocity = 150.0  # m/s
test_density = 1.225  # kg/m^2

# Import weight and location of the engine
weight_engine = database_connector.load_value("engine_weight")
engine_weight_width = 0.1
engine_thrust = database_connector.load_value("engine_max_thrust")

# Import the weight of the wing and fuel (Class II)
weight_wing = database_connector.load_value("wing_weight")
weight_fuel = database_connector.load_value("fuel_max")

# Defining where the fueltanks should be
fuel_tank_start = 0 * (wing_span / 2)
fuel_tank_engine_stop = spanwise_location_engine - 0.75
fuel_tank_engine_start = spanwise_location_engine + 0.75
fuel_tank_stop = 0.9 * (wing_span / 2)
fuel_tank_length = (fuel_tank_engine_stop - fuel_tank_start) + (fuel_tank_stop - fuel_tank_engine_start)

# Import values for the drag estimation
thickness_to_chord_ratio = database_connector.load_value("thickness_to_chord_ratio")
cd_0 = database_connector.load_value("cd0")

include_fuel_tanks = True
include_engine = True


# Define the lift and drag distribution
def lift_distribution(y, length_step, density, velocity):
    return aerodynamic_data.lift_coef_function_10(y) * 0.5 * density * (velocity ** 2) * aerodynamic_data.chord_function(y) * length_step


def drag_distribution(y, length_step, density, velocity):
    # TODO check if drag_induced is right
    return (aerodynamic_data.drag_induced_function_10(y) + cd_0) * 0.5 * density * (velocity ** 2) * aerodynamic_data.chord_function(y) * length_step


def pitching_moment_function(y, density, velocity, length_step):
    #0.5 rho V^2 S c
    print(aerodynamic_data.moment_coef_function_10(y))
    return -aerodynamic_data.moment_coef_function_10(y) * 0.5 * density * (velocity**2) *aerodynamic_data.chord_function(y) * length_step * aerodynamic_data.chord_function(y)


# Calculate the final force distribution
def z_final_force_distribution(y, length_step, density, velocity):
    value = lift_distribution(y, length_step, density, velocity) # - weight_wing / surface_area * aerodynamic_data.chord_function(y) * length_step
    if ((fuel_tank_start < y < fuel_tank_engine_stop) or (fuel_tank_engine_start < y < fuel_tank_stop)) and include_fuel_tanks:
        value -= weight_fuel / (fuel_tank_length / length_step)
    if spanwise_location_engine - length_step / 2 < y < spanwise_location_engine + length_step / 2 and include_engine:
        value -= weight_engine
    return value


# TODO Add contribution due to thrust
def x_final_force_distribution(y, length_step, density, velocity):
    return drag_distribution(y, length_step, density, velocity)


# Adding the point load of the engine after integrating
def add_engine_moment(y, length_step, moment_arm):
    if spanwise_location_engine + length_step/2 > y:
        return moment_arm * weight_engine
    else:
        return 0


def add_thrust_moment(y, length_step, moment_arm):
    if spanwise_location_engine + length_step/2 > y:
        return moment_arm * engine_thrust
    else:
        return 0


# Spanwise locations to move through for graphs
spanwise_locations_list = np.arange(radius_fuselage, wing_span / 2, global_length_step)
# spanwise_locations_list = np.arange(0, 10, global_length_step)

"""
Sign-convention:
x: towards nose
y: towards tip
z: upwards
counterclockwise
"""


# Setting up the integrals
# x_shear_integral = Integration(z_final_force_distribution, min(spanwise_locations_list), max(spanwise_locations_list))
# x_moment_integral = Integration(x_shear_integral.get_value, min(spanwise_locations_list), max(spanwise_locations_list))

x_shear_integral = Integration(z_final_force_distribution, min(spanwise_locations_list), max(spanwise_locations_list), flip_sign=True)
x_moment_integral = Integration(x_shear_integral.get_value, min(spanwise_locations_list), max(spanwise_locations_list), flip_sign=True)

z_shear_integral = Integration(x_final_force_distribution, min(spanwise_locations_list), max(spanwise_locations_list), flip_sign=True)
z_moment_integral = Integration(z_shear_integral.get_value, min(spanwise_locations_list), max(spanwise_locations_list), flip_sign=True)


# Data list for the results
z_force_data = []
x_shear_force_data = []
x_moment_data = []

x_force_data = []
z_shear_force_data = []
z_moment_data = []

y_torsion_data = []

# Time keeping
start_time_1 = time.time()

print("Calculating shear and moment.\nIntegrating... (this can take a while)")

# For every spanwise location, first integrate to shear then integrate to moment
# TODO check signs
for spanwise_location in spanwise_locations_list:
    z_force_data.append(z_final_force_distribution(spanwise_location, global_length_step, test_density, test_velocity))
    x_force_data.append(x_final_force_distribution(spanwise_location, global_length_step, test_density, test_velocity))

    x_shear_force_data.append(x_shear_integral.integrate(spanwise_location, global_length_step, test_density, test_velocity))
    x_moment_data.append(x_moment_integral.integrate(spanwise_location, global_length_step, test_density, test_velocity))

    z_shear_force_data.append(z_shear_integral.integrate(spanwise_location, global_length_step, test_density, test_velocity))
    z_moment_data.append(z_moment_integral.integrate(spanwise_location, global_length_step, test_density, test_velocity))

    y_torsion_data.append(pitching_moment_function(spanwise_location, test_density, test_velocity, global_length_step) + add_engine_moment(spanwise_location,global_length_step, moment_arm_engine) - add_thrust_moment(spanwise_location, global_length_step, moment_arm_thrust))

# More time keeping & printing
print(f"total time: {(time.time() - start_time_1) / 60:.3f} min")
print(f"LUT lengths: {len(x_shear_integral.LUT)}, {len(x_moment_integral.LUT)}, {len(z_shear_integral.LUT)}, {len(z_moment_integral.LUT)}")

# Make plots for the x direction
plt.subplot(421)
plt.title("lift and weight")
plt.plot(spanwise_locations_list, z_force_data, label="Force")
plt.ylabel("Applied Force in z (N)\nWithout point forces")
plt.xlabel("Wing location (m)")
plt.subplot(423)
plt.plot(spanwise_locations_list, x_shear_force_data, label="Shear")
plt.ylabel("Shear force in x (N)")
plt.xlabel("Wing location (m)")
plt.subplot(425)
plt.plot(spanwise_locations_list, x_moment_data, label="Moment")
plt.ylabel("Moment in x (Nm)")
plt.xlabel("Wing location (m)")

# Make plots for the z direction
plt.subplot(422)
plt.title("drag and (thrust)")
plt.plot(spanwise_locations_list, x_force_data, label="Force")
plt.ylabel("Applied Force in x (N)\nWithout point forces")
plt.xlabel("Wing location (m)")
plt.subplot(424)
plt.plot(spanwise_locations_list, z_shear_force_data, label="Shear")
plt.ylabel("Shear force in z (N)")
plt.xlabel("Wing location (m)")
plt.subplot(426)
plt.plot(spanwise_locations_list, z_moment_data, label="Moment")
plt.ylabel("Moment in z (Nm)")
plt.xlabel("Wing location (m)")

#Make plots for the u direction (torsion)
plt.subplot(427)
plt.plot(spanwise_locations_list, y_torsion_data, label="Torsion")
plt.ylabel("Torsion in y (Nm)")
plt.xlabel("Wing location (m)")

# show and pop plots
plt.show()
