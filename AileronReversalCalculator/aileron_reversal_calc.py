try:
    from Database.database_functions import DatabaseConnector
    import Importer.xflr5 as aerodynamic_data
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    import Importer.xflr5 as aerodynamic_data


# assumptions:
#   shear centre coincides with centroid
#   two-dimensional flow

# Needed variables
#   dCL/dXi (XFOIL)
#   dCM0/dXi (XFOIL)
#   density & velocity (cruise & sea level)
#   surface area (database)
#   chord @ aileron (chord function)
#   K = GJ
#   e = distance c/4 and shear center (geometry)
#   G
#   J

def get_polar_moment_of_inertia():
    return 1
