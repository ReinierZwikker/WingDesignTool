import numpy as np

try:
    from InertialLoadingCalculator.inertial_loading_calculator import calculate_inertial_loading, z_final_force_distribution, spanwise_locations_list
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from InertialLoadingCalculator.inertial_loading_calculator import calculate_inertial_loading


def absmax(lst):
    lst_max = max(lst)
    lst_min = min(lst)
    if lst_max > abs(lst_min):
        return lst_max
    else:
        return lst_min

def iterate():
    speed_min = 50  # stall speed
    speed_max = 300
    speed_step = 10

    fuel_level_min = 0
    fuel_level_max = 1
    fuel_level_step = 0.1

    density_min = 0
    density_max = 1.255
    density_step = 0.1

    speed_list = np.arange(speed_min, speed_max, speed_step)
    fuel_level_list = np.arange(fuel_level_min, fuel_level_max, fuel_level_step)
    density_list = np.arange(density_min, density_max, density_step)

    max_force_list = []
    conditions = []

    print(f"total iterations: {len(speed_list)*len(fuel_level_list)*len(density_list)}")

    for speed in speed_list:
        for fuel_level in fuel_level_list:
            for density in density_list:
                z_force_data = []
                for spanwise_location in spanwise_locations_list:
                    z_force_data.append(z_final_force_distribution(spanwise_location, 1, density, speed, fuel_level))
                print(absmax(z_force_data))
                conditions.append((speed, density, fuel_level))
                max_force_list.append(absmax(z_force_data))

    max_force = absmax(max_force_list)
    max_conditions = conditions[max_force_list.index(max_force)]
    print(f"max:  {max_force}, \nconditions: {max_conditions}")

iterate()