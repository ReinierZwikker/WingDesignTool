try:
    from Database.database_functions import DatabaseConnector
    import Importer.xflr5 as aerodynamic_data
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    import Importer.xflr5 as aerodynamic_data

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

inboard_aileron_start = database_connector.load_value("inboard_aileron_start")
inboard_aileron_end = database_connector.load_value("inboard_aileron_end")
#choose midpoint of the aileron
chord_inboard_aileron = aerodynamic_data.chord_function(inboard_aileron_start + (inboard_aileron_end-inboard_aileron_start)/2)

outboard_aileron_start = database_connector.load_value("outboard_aileron_start")
outboard_aileron_end = database_connector.load_value("outboard_aileron_end")
#choose midpoint of the aileron
chord_outboard_aileron = aerodynamic_data.chord_function(outboard_aileron_start + (outboard_aileron_end-outboard_aileron_start)/2)

wing_surface_area = database_connector.load_value("surface_area")

#material: AL6061-T6
shear_modulus = 26 * 10**9  #Pa (Source: http://asm.matweb.com/search/SpecificMaterial.asp?bassnum=MA6061T6)

#For exact location multiply by the chord length
wing_box_centroid_x = database_connector.load_value("wing_box_centroid_x")
wing_box_centroid_z = database_connector.load_value("wing_box_centroid_z")



inboard_aileron_amount_of_stringers = ''
outboard_aileron_amount_of_stringers = ''

def get_polar_moment_of_inertia():
    return 1
