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

# #Wing box configuration: heavy plates
# thickness_plates= 0.045 #m
# width_wing_box = 1.0    #m
# height_wing_box = 1.0   #m
# thickness_spars = 0.03  #m
#
# number_stringers = 1
# area_stringer = 0.001   #m2
# number_ribs = 1
# area_ribs = 1.0  #m2


