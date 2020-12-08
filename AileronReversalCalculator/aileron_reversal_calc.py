try:
    from Database.database_functions import DatabaseConnector
    import Importer.xflr5 as aerodynamic_data
    from CentroidCalculator.centroid_calculator import get_centroid
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    import Importer.xflr5 as aerodynamic_data
    from CentroidCalculator.centroid_calculator import get_centroid

import math
database_connector = DatabaseConnector()
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



def get_distance_e(chord_length,x_coordinate_wingbox):
    #distance wrt leading edge
    return 0.25 - x_coordinate_wingbox/chord_length

def get_aileron_reversal_speed():
    #inboard
    inboard_aileron_start = database_connector.load_value("inboard_aileron_start")
    inboard_aileron_end = database_connector.load_value("inboard_aileron_end")
    # choose midpoint of the aileron
    chord_length_inboard_aileron = aerodynamic_data.chord_function(
    inboard_aileron_start + (inboard_aileron_end - inboard_aileron_start) / 2)

    #outboard
    outboard_aileron_start = database_connector.load_value("outboard_aileron_start")
    outboard_aileron_end = database_connector.load_value("outboard_aileron_end")
    # choose midpoint of the aileron
    chord_length_outboard_aileron = aerodynamic_data.chord_function(
    outboard_aileron_start + (outboard_aileron_end - outboard_aileron_start) / 2)

    wing_surface_area = database_connector.load_value("surface_area")

    # material: AL6061-T6
    shear_modulus = 26 * 10 ** 9  # Pa (Source: http://asm.matweb.com/search/SpecificMaterial.asp?bassnum=MA6061T6)
        #more variables
    K = shear_modulus * torsional_stiffness
    ratio_dCL_dXi =
    ratio_dCM0_dXi =
    CL_alpha = database_connector.load_value("cl-alpha-curve")  #rad
    density_sea_level = 1.225   #kg/m3
    density_cruise_level = database_connector.load_value("density_cruise_level")

    reversal_speed_inboard_cruise = math.sqrt( (-K * ratio_dCL_dXi)/(0.5*density_cruise_level*wing_surface_area*chord_length_inboard_aileron*ratio_dCM0_dXi*CL_alpha) )
    reversal_speed_inboard_sea_level = math.sqrt( (-K * ratio_dCL_dXi)/(0.5*density_sea_level*wing_surface_area*chord_length_inboard_aileron*ratio_dCM0_dXi*CL_alpha) )
    reversal_speed_outboard_sea_level = math.sqrt( (-K * ratio_dCL_dXi)/(0.5*density_sea_level*wing_surface_area*chord_length_outboard_aileron*ratio_dCM0_dXi*CL_alpha) )

    #print statements
    print("The aileron reversal speed of the inboard aileron at cruise level [m/s]: ")
    print(reversal_speed_inboard_cruise)
    print("\nThe aileron reversal speed of the inboard aileron at sea level [m/s]: ")
    print(reversal_speed_inboard_sea_level)
    print("\nThe aileron reversal speed of the outboard aileron at sea level [m/s]: ")
    print(reversal_speed_outboard_sea_level)

    return reversal_speed_inboard_cruise,reversal_speed_inboard_sea_level,reversal_speed_outboard_sea_level

def get_aileron_effectiveness():
    # inboard
    inboard_aileron_start = database_connector.load_value("inboard_aileron_start")
    inboard_aileron_end = database_connector.load_value("inboard_aileron_end")
    # choose midpoint of the aileron
    chord_length_inboard_aileron = aerodynamic_data.chord_function(
        inboard_aileron_start + (inboard_aileron_end - inboard_aileron_start) / 2)

    # outboard
    outboard_aileron_start = database_connector.load_value("outboard_aileron_start")
    outboard_aileron_end = database_connector.load_value("outboard_aileron_end")
    # choose midpoint of the aileron
    chord_length_outboard_aileron = aerodynamic_data.chord_function(
        outboard_aileron_start + (outboard_aileron_end - outboard_aileron_start) / 2)

    #more variables
    wing_surface_area = database_connector.load_value("surface_area")
    # material: AL6061-T6
    shear_modulus = 26 * 10 ** 9  # Pa (Source: http://asm.matweb.com/search/SpecificMaterial.asp?bassnum=MA6061T6)
    K = shear_modulus * torsional_stiffness
    ratio_dCL_dXi =
    ratio_dCM0_dXi =
    CL_alpha = database_connector.load_value("cl-alpha-curve")  # rad
    density_sea_level = 1.225  # kg/m3
    velocity_sea_level =
    density_cruise_level = database_connector.load_value("density_cruise_level")
    velocity_cruise_level =

    aileron_effectiveness_inboard_cruise = ((0.5*density_cruise_level*velocity_cruise_level**2*wing_surface_area*chord_length_inboard_aileron*ratio_dCM0_dXi*ratio_dCL_dXi+K*ratio_dCL_dXi)/
                                            ((K-0.5*density_cruise_level*velocity_cruise_level**2*wing_surface_area*chord_length_inboard_aileron*get_distance_e(chord_length_inboard_aileron)*CL_alpha)*ratio_dCL_dXi))

    aileron_effectiveness_inboard_sea_level =((0.5*density_sea_level*velocity_sea_level**2*wing_surface_area*chord_length_inboard_aileron*ratio_dCM0_dXi*ratio_dCL_dXi+K*ratio_dCL_dXi)/
                                            ((K-0.5*density_sea_level*velocity_sea_level**2*wing_surface_area*chord_length_inboard_aileron*get_distance_e(chord_length_inboard_aileron)*CL_alpha)*ratio_dCL_dXi))

    aileron_effectiveness_outboard_sea_level = ((0.5*density_sea_level*velocity_sea_level**2*wing_surface_area*chord_length_outboard_aileron*ratio_dCM0_dXi*ratio_dCL_dXi+K*ratio_dCL_dXi)/
                                            ((K-0.5*density_sea_level*velocity_sea_level**2*wing_surface_area*chord_length_outboard_aileron*get_distance_e(chord_length_outboard_aileron)*CL_alpha)*ratio_dCL_dXi))

    #print statements
    print("\nThe aileron effectiveness for inboard aileron at cruise [m/s]: ")
    print(aileron_effectiveness_inboard_cruise)
    print("\nThe aileron effectiveness for inboard aileron at sea level [m/s]: ")
    print(aileron_effectiveness_inboard_sea_level)
    print("\nThe aileron effectiveness for outboard aileron at sea level [m/s]: ")
    print(aileron_effectiveness_outboard_sea_level)
    return aileron_effectiveness_inboard_cruise,aileron_effectiveness_inboard_sea_level,aileron_effectiveness_outboard_sea_level

get_aileron_reversal_speed()
get_aileron_effectiveness()