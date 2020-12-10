### ------ Workpackage 4.1: Inertial loading calculations ------ ###
import numpy as np
import time
import matplotlib.pyplot as plt
import pickle

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
wing_span = database_connector.load_value("wing_span") / 2
outer_diameter = database_connector.load_value("df,outer")
radius_fuselage = outer_diameter / 2
surface_area = database_connector.load_value("surface_area") / 2
root_chord = database_connector.load_value("root_chord")
tip_chord = database_connector.load_value("tip_chord")
taper_ratio = database_connector.load_value("taper_ratio")
spanwise_location_engine = database_connector.load_value("engine_spanwise_location")

chord_at_engine_location = aerodynamic_data.chord_function(spanwise_location_engine)
radius_engine = database_connector.load_value("d_engine") / 2

moment_arm_engine = (0.25 + 0.2) * aerodynamic_data.chord_function(spanwise_location_engine)
moment_arm_thrust = 1.5 * radius_engine

global_length_step = 0.1  # [m]

# Define the flight conditions
test_velocity = 236.32  # m/s
test_density = 1.225  # kg/m^2
lift_coef_function = aerodynamic_data.lift_coef_function_10
drag_induced_function = aerodynamic_data.drag_induced_function_10
moment_coef_function = aerodynamic_data.moment_coef_function_10

# Import weight and location of the engine
weight_engine = database_connector.load_value("engine_weight")
engine_thrust = database_connector.load_value("engine_max_thrust") / 2

# Import the weight of the wing and fuel (Class II)
weight_wing = database_connector.load_value("wing_weight") / 2
weight_fuel = database_connector.load_value("fuel_max") / 2

# Defining where the fuel tanks should be
fuel_tank_start = 0 * wing_span
fuel_tank_engine_stop = spanwise_location_engine - 0.25
fuel_tank_engine_start = spanwise_location_engine + 0.25
fuel_tank_stop = 0.9 * wing_span
fuel_tank_length = (fuel_tank_engine_stop - fuel_tank_start) + (fuel_tank_stop - fuel_tank_engine_start)

# Import values for the drag estimation
thickness_to_chord_ratio = database_connector.load_value("thickness_to_chord_ratio")
cd_0 = database_connector.load_value("cd0")

include_fuel_tanks = True
include_engine = True
fuel_tank_level = 1  # level of the fuel tanks from 0 to 1

load_factor = 4.3


# Define the lift and drag distribution
def lift_distribution(y, length_step, density, velocity):
    return load_factor * lift_coef_function(y) * 0.5 * density * (velocity ** 2) * aerodynamic_data.chord_function(y)


def drag_distribution(y, length_step, density, velocity):
    return load_factor * (drag_induced_function(y) + cd_0) * 0.5 * density * (velocity ** 2) * aerodynamic_data.chord_function(y)


def pitching_moment_function(y, density, velocity, length_step):
    # 0.5 rho V^2 S c
    # print(aerodynamic_data.moment_coef_function_10(y))
    return load_factor * moment_coef_function(y) * 0.5 * density * (velocity ** 2) * aerodynamic_data.chord_function(y) * \
           aerodynamic_data.chord_function(y)


# Calculate the final force distribution
def z_final_force_distribution(y, length_step, density, velocity):
    value = lift_distribution(y, length_step, density, velocity) - weight_wing / surface_area * aerodynamic_data.chord_function(y)
    if ((fuel_tank_start < y < fuel_tank_engine_stop) or (fuel_tank_engine_start < y < fuel_tank_stop)) and include_fuel_tanks:
        value -= (weight_fuel / fuel_tank_length) * fuel_tank_level
    if spanwise_location_engine - length_step / 2 < y < spanwise_location_engine + length_step / 2 and include_engine:
        value -= weight_engine
    return value


# TODO Add contribution due to thrust
def x_final_force_distribution(y, length_step, density, velocity, include_thrust=include_engine):
    value = drag_distribution(y, length_step, density, velocity)
    if spanwise_location_engine - length_step / 2 < y < spanwise_location_engine + length_step / 2 and include_thrust:
        value -= engine_thrust
    return value


# Adding the point load of the engine after integrating
def add_engine_moment(y, length_step, moment_arm):
    if spanwise_location_engine + length_step / 2 > y:
        return moment_arm * weight_engine
    else:
        return 0


def add_thrust_moment(y, length_step, moment_arm):
    if spanwise_location_engine + length_step / 2 > y:
        return moment_arm * engine_thrust
    else:
        return 0


# Spanwise locations to move through for graphs
spanwise_locations_list = np.arange(radius_fuselage, wing_span, global_length_step)

"""
Sign-convention:
x: towards nose
y: towards tip
z: upwards
counterclockwise
"""

# Setting up the integrals
x_shear_integral = Integration(z_final_force_distribution, min(spanwise_locations_list), max(spanwise_locations_list), flip_sign=True)
x_moment_integral = Integration(x_shear_integral.get_value, min(spanwise_locations_list), max(spanwise_locations_list), flip_sign=True)

z_shear_integral = Integration(x_final_force_distribution, min(spanwise_locations_list), max(spanwise_locations_list), flip_sign=True)
z_moment_integral = Integration(z_shear_integral.get_value, min(spanwise_locations_list), max(spanwise_locations_list), flip_sign=True)


def calculate_inertial_loading(length_step):
    # Data list for the results
    z_force_data = []
    x_shear_force_data = []
    x_moment_data = []

    x_force_data = []
    x_force_data_without_thrust = []
    z_shear_force_data = []
    z_moment_data = []

    y_torsion_data = []

    # Time keeping
    start_time_1 = time.time()

    print("Calculating shear and moment./nIntegrating... (this can take a while)")

    # For every spanwise location, first integrate to shear then integrate to moment
    for spanwise_location in spanwise_locations_list:
        z_force_data.append(z_final_force_distribution(spanwise_location, length_step, test_density, test_velocity))
        x_force_data.append(x_final_force_distribution(spanwise_location, length_step, test_density, test_velocity))
        x_force_data_without_thrust.append(
            x_final_force_distribution(spanwise_location, length_step, test_density, test_velocity, include_thrust=False))

        x_shear_force_data.append(x_shear_integral.integrate(spanwise_location, length_step, length_step, test_density, test_velocity))
        x_moment_data.append(x_moment_integral.integrate(spanwise_location, length_step, length_step, test_density, test_velocity))

        z_shear_force_data.append(z_shear_integral.integrate(spanwise_location, length_step, length_step, test_density, test_velocity))
        z_moment_data.append(z_moment_integral.integrate(spanwise_location, global_length_step, length_step, test_density, test_velocity))

        y_torsion_data.append(
            pitching_moment_function(spanwise_location, test_density, test_velocity, length_step) + add_engine_moment(spanwise_location, length_step,
                                                                                                                      moment_arm_engine) - add_thrust_moment(
                spanwise_location, length_step, moment_arm_thrust))

    # More time keeping & printing
    print(f"Total integration time: {(time.time() - start_time_1) / 60:.3f} min")
    print(f"LUT lengths: {len(x_shear_integral.LUT)}, {len(x_moment_integral.LUT)}, {len(z_shear_integral.LUT)}, {len(z_moment_integral.LUT)}")

    # Saving results
    with open('./data.pickle', 'wb') as file:
        pickle.dump((spanwise_locations_list, z_force_data, x_shear_force_data, x_moment_data, x_force_data, z_shear_force_data, z_moment_data,
                     y_torsion_data), file)

    return z_force_data, x_force_data, x_force_data_without_thrust, x_shear_force_data, x_moment_data, z_shear_force_data, z_moment_data, y_torsion_data


def plot_inertial_loading(z_force_data, x_force_data, x_force_data_without_thrust, x_shear_force_data, x_moment_data, z_shear_force_data,
                          z_moment_data, y_torsion_data):
    fig, axs = plt.subplots(4, 2)

    fig.suptitle(f"Inertial Loading for V={test_velocity} [m/s] at rho={test_density} [kg/m3] using steps of "
                 f"{spanwise_locations_list[1] - spanwise_locations_list[0]:0.3f} [m]",
                 fontsize=20)
    # Make plots for the x direction
    fig.subplots_adjust(left=0.07, bottom=0.07, right=0.97, top=0.90, wspace=0.10, hspace=0.30)
    axs[0, 0].set_title("z: Lift and Weight")
    axs[0, 0].plot(spanwise_locations_list, [x / 1000 for x in z_force_data], label="Force")
    axs[0, 0].set_ylabel("Applied Force in z (kN)")

    axs[1, 0].set_title("x: Shear due to Lift and Weight")
    axs[1, 0].plot(spanwise_locations_list, [x / 1000 for x in x_shear_force_data], label="Shear")
    axs[1, 0].set_ylabel("Shear force in x (kN)")

    axs[2, 0].set_title("x: Moment due to Lift and Weight")
    axs[2, 0].plot(spanwise_locations_list, [x / 1000 for x in x_moment_data], label="Moment")
    axs[2, 0].set_ylabel("Moment in x (kNm)")

    # Make plots for the z direction
    axs[0, 1].set_title("x: Drag without Thrust")
    axs[0, 1].plot(spanwise_locations_list, [x / 1000 for x in x_force_data_without_thrust], label="Force")
    axs[0, 1].set_ylabel("Applied Force in x (kN)")

    axs[1, 1].set_title("x: Drag and Thrust")
    axs[1, 1].plot(spanwise_locations_list, [x / 1000 for x in x_force_data], label="Force")
    axs[1, 1].set_ylabel("Applied Force in x (kN)")

    axs[2, 1].set_title("z: Shear due to Drag and Thrust")
    axs[2, 1].plot(spanwise_locations_list, [x / 1000 for x in z_shear_force_data], label="Shear")
    axs[2, 1].set_ylabel("Shear force in z (kN)")

    axs[3, 1].set_title("z: Moment due to Drag and Thrust")
    axs[3, 1].plot(spanwise_locations_list, [x / 1000 for x in z_moment_data], label="Moment")
    axs[3, 1].set_ylabel("Moment in z (kNm)")
    axs[3, 1].set_xlabel("Wing location (m)")

    # Make plots for the u direction (torsion)
    axs[3, 0].set_title("u: Torsion")
    axs[3, 0].plot(spanwise_locations_list, [x / 1000 for x in y_torsion_data], label="Torsion")
    axs[3, 0].set_ylabel("Torsion in y (kNm)")
    axs[3, 0].set_xlabel("Wing location (m)")

    # show and pop plots
    plt.show()


# UNCOMMENT THIS TO PLOT INERTIAL LOADING:
print(min(calculate_inertial_loading(global_length_step)[6]))
plot_inertial_loading(*calculate_inertial_loading(global_length_step))
