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


spanwise_location = 1.0 #int(input("spanwise location [m]? "))
chord_length = 1.0 #aerodynamic_data.chord_function(spanwise_location)

##wing box configuration
wingbox_corner_points = database_connector.load_wingbox_value("wingbox_corner_points")
left_top_corner_wingbox = wingbox_corner_points[0]
left_bottom_corner_wingbox = wingbox_corner_points[3]
right_top_corner_wingbox = wingbox_corner_points[1]
right_bottom_corner_wingbox = wingbox_corner_points[2]

width_wingbox = (right_top_corner_wingbox[0] - left_top_corner_wingbox[0]) * chord_length
height_front_spar =(left_top_corner_wingbox[1] - left_bottom_corner_wingbox[1]) * chord_length
height_back_spar = (right_top_corner_wingbox[1] - right_bottom_corner_wingbox[1]) * chord_length
area_wingbox = width_wingbox * height_front_spar - (width_wingbox * (height_front_spar - height_back_spar))/2


plate_thickness = database_connector.load_wingbox_value("plate_thickness")
spar_thickness = database_connector.load_wingbox_value("spar_thickness")

stringer_area = database_connector.load_wingbox_value("stringer_area")



#x coordinate centroid (wrt LE-chord intersection)


