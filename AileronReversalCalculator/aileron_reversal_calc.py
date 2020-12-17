try:
    from Database.database_functions import DatabaseConnector
    import Importer.xflr5 as aerodynamic_data
    from CentroidCalculator.centroid_calculator import get_centroid
    from CentroidCalculator.polar_moment_calculator import get_polar_moment_of_inertia
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    import Importer.xflr5 as aerodynamic_data
    from CentroidCalculator.centroid_calculator import get_centroid
    from CentroidCalculator.polar_moment_calculator import get_polar_moment_of_inertia

database_connector = DatabaseConnector()
import math
import matplotlib.pyplot as plt

# assumptions:
#   shear centre coincides with centroid
#   two-dimensional flow

# Needed variables
#   dCL/dXi (XFOIL)
#   dCM0/dXi (XFOIL)
#   density & velocity (cruise & sea level)
#   surface area (database)    check
#   chord @ aileron (chord function)    check
#   K = GJ
#   e = distance c/4 and shear center (geometry)
#   G = shear modulus    check
#   J = polar moment (calculate)



def get_distance_e(chord_length,x_coordinate_centroid_wingbox):
    #distance wrt leading edge
    return 0.25 - x_coordinate_centroid_wingbox/chord_length

def get_aileron_reversal_speed():
    #inboard
    inboard_aileron_start = database_connector.load_value("inboard_aileron_start")
    inboard_aileron_end = database_connector.load_value("inboard_aileron_end")
    # choose midpoint of the aileron
    spanwise_location_inboard = inboard_aileron_start + (inboard_aileron_end - inboard_aileron_start) / 2
    chord_length_inboard_aileron = aerodynamic_data.chord_function(spanwise_location_inboard)

    #outboard
    outboard_aileron_start = database_connector.load_value("outboard_aileron_start")
    outboard_aileron_end = database_connector.load_value("outboard_aileron_end")
    # choose midpoint of the aileron
    spanwise_location_outboard = outboard_aileron_start + (outboard_aileron_end - outboard_aileron_start) / 2
    chord_length_outboard_aileron = aerodynamic_data.chord_function(spanwise_location_outboard)
    # print(chord_length_outboard_aileron)
    # print(chord_length_inboard_aileron)


    wing_surface_area = database_connector.load_value("surface_area")

    # material: AL6061-T6
    shear_modulus = 26 * 10**6  # Pa (Source: http://asm.matweb.com/search/SpecificMaterial.asp?bassnum=MA6061T6)
    #more variables
    torsional_stiffness_inboard = get_polar_moment_of_inertia(spanwise_location_inboard)
    K_inboard = shear_modulus * torsional_stiffness_inboard
    print(K_inboard * 10**-6)
    torsional_stiffness_outboard = get_polar_moment_of_inertia(spanwise_location_outboard)
    K_outboard = shear_modulus * torsional_stiffness_outboard
    print(K_outboard * 10**-6)
    CL_alpha = database_connector.load_value("cl-alpha_curve")  #rad
    density_sea_level = 1.225   #kg/m3
    density_cruise_level = database_connector.load_value("density_cruise_level")

    dCL_dXi_inboard_sealevel = database_connector.load_value("dcl_dxi_inboard_sl")
    dCL_dXi_outboard_sealevel = database_connector.load_value("dcl_dxi_outboard_sl")
    dCL_dXi_inboard_cruise = database_connector.load_value("dcl_dxi_inboard_cruise")

    # dCL_dXi_inboard_sealevel = 0.8
    # dCL_dXi_outboard_sealevel = 0.8
    # dCL_dXi_inboard_cruise = 0.8

    dCM_dXi_inboard_sealevel = database_connector.load_value("dcm_dxi_inboard_sl")
    dCM_dXi_outboard_sealevel = database_connector.load_value("dcm_dxi_outboard_sl")
    dCM_dXi_inboard_cruise = database_connector.load_value("dcm_dxi_inboard_cruise")

    # dCM_dXi_inboard_sealevel = database_connector.load_value("dcm_dxi_inboard_sl")
    # dCM_dXi_outboard_sealevel = database_connector.load_value("dcm_dxi_outboard_sl")
    # dCM_dXi_inboard_cruise = -0.25

    reversal_speed_inboard_cruise = math.sqrt( (-K_inboard * dCL_dXi_inboard_cruise)/(0.5*density_cruise_level*wing_surface_area*chord_length_inboard_aileron*dCM_dXi_inboard_cruise*CL_alpha) )
    reversal_speed_inboard_sea_level = math.sqrt( (-K_inboard * dCL_dXi_inboard_sealevel)/(0.5*density_sea_level*wing_surface_area*chord_length_inboard_aileron*dCM_dXi_inboard_sealevel*CL_alpha) )
    reversal_speed_outboard_sea_level = math.sqrt( (-K_outboard * dCL_dXi_outboard_sealevel)/(0.5*density_sea_level*wing_surface_area*chord_length_outboard_aileron*dCM_dXi_outboard_sealevel*CL_alpha) )

    #print statements
    print("The aileron reversal speed of the inboard aileron at cruise level [m/s]: ")
    print(reversal_speed_inboard_cruise)
    print("\nThe aileron reversal speed of the inboard aileron at sea level [m/s]: ")
    print(reversal_speed_inboard_sea_level)
    print("\nThe aileron reversal speed of the outboard aileron at sea level [m/s]: ")
    print(reversal_speed_outboard_sea_level)

    return reversal_speed_inboard_cruise,reversal_speed_inboard_sea_level,reversal_speed_outboard_sea_level

def get_aileron_effectiveness(range_velocity_cruise,range_velocity_sealevel):
    # inboard
    inboard_aileron_start = database_connector.load_value("inboard_aileron_start")
    inboard_aileron_end = database_connector.load_value("inboard_aileron_end")
    # choose midpoint of the aileron
    spanwise_location_inboard = inboard_aileron_start + (inboard_aileron_end - inboard_aileron_start) / 2
    chord_length_inboard_aileron = aerodynamic_data.chord_function(spanwise_location_inboard)

    # outboard
    outboard_aileron_start = database_connector.load_value("outboard_aileron_start")
    outboard_aileron_end = database_connector.load_value("outboard_aileron_end")
    # choose midpoint of the aileron
    spanwise_location_outboard = outboard_aileron_start + (outboard_aileron_end - outboard_aileron_start) / 2
    chord_length_outboard_aileron = aerodynamic_data.chord_function(spanwise_location_outboard)

    #more variables
    wing_surface_area = database_connector.load_value("surface_area")
    # material: AL6061-T6
    shear_modulus = 26 * 10 ** 9  # Pa (Source: http://asm.matweb.com/search/SpecificMaterial.asp?bassnum=MA6061T6)
    torsional_stiffness_inboard = get_polar_moment_of_inertia(spanwise_location_inboard)
    K_inboard = shear_modulus * torsional_stiffness_inboard
    torsional_stiffness_outboard = get_polar_moment_of_inertia(spanwise_location_outboard)
    K_outboard = shear_modulus * torsional_stiffness_outboard
    CL_alpha = database_connector.load_value("cl-alpha_curve")  # rad

    dCL_dXi_inboard_sealevel = database_connector.load_value("dcl_dxi_inboard_sl")
    dCL_dXi_outboard_sealevel = database_connector.load_value("dcl_dxi_outboard_sl")
    dCL_dXi_inboard_cruise = database_connector.load_value("dcl_dxi_inboard_cruise")

    dCM_dXi_inboard_sealevel = database_connector.load_value("dcm_dxi_inboard_sl")
    dCM_dXi_outboard_sealevel = database_connector.load_value("dcm_dxi_outboard_sl")
    dCM_dXi_inboard_cruise = database_connector.load_value("dcm_dxi_inboard_cruise")

    x_coordinate_centroid_inboard = get_centroid(spanwise_location_inboard)[0]
    x_coordinate_centroid_outboard = get_centroid(spanwise_location_outboard)[0]

    #cruise
    velocity_cruise_lst = []
    aileron_effectiveness_inboard_cruise_lst = []
    for velocity in range(range_velocity_cruise+1):
        density_cruise_level = database_connector.load_value("density_cruise_level")
        aileron_effectiveness_inboard_cruise = ((0.5 * density_cruise_level * velocity ** 2 * wing_surface_area * chord_length_inboard_aileron * dCM_dXi_inboard_cruise * dCL_dXi_inboard_cruise + K_inboard * dCL_dXi_inboard_cruise) /
                                                ((K_inboard - 0.5 * density_cruise_level * velocity ** 2 * wing_surface_area * chord_length_inboard_aileron * get_distance_e(
                                                         chord_length_inboard_aileron,x_coordinate_centroid_inboard) * CL_alpha) * dCL_dXi_inboard_cruise))
        velocity_cruise_lst.append(velocity)
        aileron_effectiveness_inboard_cruise_lst.append(aileron_effectiveness_inboard_cruise)

    #sea level
    velocity_sealevel_lst = []
    aileron_effectiveness_inboard_sealevel_lst = []
    aileron_effectiveness_outboard_sealevel_lst = []
    for velocity in range(range_velocity_sealevel+1):
        density_sea_level = 1.225
        aileron_effectiveness_inboard_sea_level = ((0.5 * density_sea_level * velocity ** 2 * wing_surface_area * chord_length_inboard_aileron * dCM_dXi_inboard_sealevel * dCL_dXi_inboard_sealevel + K_inboard * dCL_dXi_inboard_sealevel) /
                                               ((K_inboard - 0.5 * density_sea_level * velocity ** 2 * wing_surface_area * chord_length_inboard_aileron * get_distance_e(
                                                        chord_length_inboard_aileron,x_coordinate_centroid_inboard) * CL_alpha) * dCL_dXi_inboard_sealevel))

        aileron_effectiveness_outboard_sea_level = ((0.5 * density_sea_level * velocity ** 2 * wing_surface_area * chord_length_outboard_aileron * dCM_dXi_outboard_sealevel * dCL_dXi_outboard_sealevel + K_outboard * dCL_dXi_outboard_sealevel) /
                                                ((K_outboard - 0.5 * density_sea_level * velocity ** 2 * wing_surface_area * chord_length_outboard_aileron * get_distance_e(
                                                         chord_length_outboard_aileron,x_coordinate_centroid_outboard) * CL_alpha) * dCL_dXi_outboard_sealevel))
        velocity_sealevel_lst.append(velocity)
        aileron_effectiveness_inboard_sealevel_lst.append(aileron_effectiveness_inboard_sea_level)
        aileron_effectiveness_outboard_sealevel_lst.append(aileron_effectiveness_outboard_sea_level)

    #print statements
    # print("\nThe aileron effectiveness for inboard aileron at cruise [m/s]: ")
    # print(aileron_effectiveness_inboard_cruise)
    # print("\nThe aileron effectiveness for inboard aileron at sea level [m/s]: ")
    # print(aileron_effectiveness_inboard_sea_level)
    # print("\nThe aileron effectiveness for outboard aileron at sea level [m/s]: ")
    # print(aileron_effectiveness_outboard_sea_level)
    return velocity_cruise_lst, aileron_effectiveness_inboard_cruise_lst, velocity_sealevel_lst, aileron_effectiveness_inboard_sealevel_lst, aileron_effectiveness_outboard_sealevel_lst

def plot_aileron_effectiveness(velocity_cruise_lst, aileron_effectiveness_inboard_cruise_lst, velocity_sealevel_lst, aileron_effectiveness_inboard_sealevel_lst, aileron_effectiveness_outboard_sealevel_lst):
    fig, axs = plt.subplots(2, 2)

    axs[0, 0].set_title("Aileron effectiveness for the inboard aileron at cruise level")
    axs[0, 0].plot(velocity_cruise_lst, aileron_effectiveness_inboard_cruise_lst, label="Aileron Effectiveness")
    axs[0, 0].set_xlabel("Velocity [m/s]")
    axs[0, 0].set_ylabel("Aileron effectiveness [-]")

    axs[0, 1].set_visible(False)

    axs[1, 0].set_title("Aileron effectiveness for the inboard aileron at sea level")
    axs[1, 0].plot(velocity_sealevel_lst,aileron_effectiveness_inboard_sealevel_lst, label="Aileron Effectiveness")
    axs[1, 0].set_xlabel("Velocity [m/s]")
    axs[1, 0].set_ylabel("Aileron effectiveness [-]")

    axs[1, 1].set_title("Aileron effectiveness for the outboard aileron at sea level")
    axs[1, 1].plot(velocity_sealevel_lst,aileron_effectiveness_outboard_sealevel_lst, label="Aileron Effectiveness")
    axs[1, 1].set_xlabel("Velocity [m/s]")
    axs[1, 1].set_ylabel("Aileron effectiveness [-]")

    plt.show()

get_aileron_reversal_speed()

range_cruise_velocities = 300   #m/s
range_sealevel_velocities = 300 #m/s
plot_aileron_effectiveness(*get_aileron_effectiveness(range_cruise_velocities,range_sealevel_velocities))

