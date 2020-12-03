try:
    from Database.database_functions import DatabaseConnector
    import Importer.xflr5 as aerodynamic_data
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    import Importer.xflr5 as aerodynamic_data

import math

database_connector = DatabaseConnector()


spanwise_location = 1.0 #float(input("spanwise location [m]? "))
chord_length = 1.0 #aerodynamic_data.chord_function(spanwise_location)

##wing box configuration
wingbox_corner_points = database_connector.load_wingbox_value("wingbox_corner_points")
left_top_corner_wingbox = wingbox_corner_points[0]
left_bottom_corner_wingbox = wingbox_corner_points[3]
right_top_corner_wingbox = wingbox_corner_points[1]
right_bottom_corner_wingbox = wingbox_corner_points[2]

length_top_plate = (math.sqrt((right_top_corner_wingbox[0]-left_top_corner_wingbox[0])**2 + (left_top_corner_wingbox[1]-right_top_corner_wingbox[1])**2)) * chord_length
height_front_spar =(left_top_corner_wingbox[1] - left_bottom_corner_wingbox[1]) * chord_length
height_back_spar = (right_top_corner_wingbox[1] - right_bottom_corner_wingbox[1]) * chord_length
length_bottom_plate = (math.sqrt((right_top_corner_wingbox[0]-left_top_corner_wingbox[0])**2 + (-left_bottom_corner_wingbox[1]+right_bottom_corner_wingbox[1])**2)) * chord_length
height_middle_spar = height_front_spar - math.sqrt((length_bottom_plate/2)**2 - (length_top_plate/2)**2)
#area_wingbox = length_top_plate * height_front_spar - (length_top_plate * (height_front_spar - height_back_spar))/2


plate_thickness = database_connector.load_wingbox_value("plate_thickness")
spar_thickness = database_connector.load_wingbox_value("spar_thickness")

area_front_spar = spar_thickness * height_front_spar
area_back_spar = spar_thickness * height_back_spar
area_middle_spar = spar_thickness * height_middle_spar
area_top_plate = plate_thickness * length_top_plate
area_bottom_plate = plate_thickness * length_bottom_plate

x_top_bottom_plate = (left_top_corner_wingbox[0] + right_top_corner_wingbox[0]) * chord_length/2
x_front_spar = left_top_corner_wingbox[0] * chord_length
x_back_spar = right_top_corner_wingbox[0] * chord_length
x_middle_spar = (left_top_corner_wingbox[0] + (right_top_corner_wingbox[0]-left_top_corner_wingbox[0])/2) * chord_length

z_top_plate = (left_top_corner_wingbox[1] + right_top_corner_wingbox[1]) * chord_length / 2
z_bottom_plate = (left_bottom_corner_wingbox[1] + right_bottom_corner_wingbox[1]) * chord_length / 2
z_front_spar = (left_top_corner_wingbox[1] + left_bottom_corner_wingbox[1]) * chord_length / 2
z_middle_spar = height_middle_spar / 2 + z_bottom_plate
z_back_spar = (right_top_corner_wingbox[1]+right_bottom_corner_wingbox[1]) * chord_length / 2



top_stringer_area = database_connector.load_wingbox_value("top_stringer_area")

def calculate_x_coordinate_centroid(x_lst,area_lst):
    AX_lst = []
    for index in range(len(x_lst)):
        AX_lst.append(x_lst[index] * area_lst[index])
        #element +=1

    sum_area = sum(area_lst)
    sum_AX = sum(AX_lst)
    return sum_AX/sum_area

def calculate_z_coordinate_centroid(z_lst,area_lst):
    AZ_lst = []
    for element in range(len(z_lst)):
        AZ_lst.append(z_lst[element] * area_lst[element])
    sum_area = sum(area_lst)
    sum_AZ = sum(AZ_lst)
    return sum_AZ/sum_area


area_lst = [area_top_plate,area_bottom_plate,area_front_spar,area_middle_spar,area_back_spar]
x_coordinates_lst = [x_top_bottom_plate,x_top_bottom_plate,x_front_spar,x_middle_spar,x_back_spar]
z_coordinates_lst = [z_top_plate,z_bottom_plate,z_front_spar,z_middle_spar,z_back_spar]

#coordinates centroid (wrt LE-chord intersection)
x_centroid = calculate_x_coordinate_centroid(x_coordinates_lst,area_lst)
z_centroid = calculate_z_coordinate_centroid(z_coordinates_lst,area_lst)
print([x_centroid,z_centroid])


