try:
    from Database.database_functions import DatabaseConnector
    from CentroidCalculator.centroid_funcs import get_amount_of_stringers
    import Importer.xflr5 as aerodynamic_data
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    from CentroidCalculator.centroid_funcs import get_amount_of_stringers
    import Importer.xflr5 as aerodynamic_data

import math

database_connector = DatabaseConnector()


def get_centroid(spanwise_location, verbose=False):
    """
    Calculates the X and Z component of the centroid.

    :param spanwise_location: The location of the cross-section along the span for which the centroid is calculated
    :param verbose: Print values while calculating
    :return: The centroid of the cross-section as a list of [X, Z]
    """
    chord_length = aerodynamic_data.chord_function(spanwise_location)

    # wing box configuration
    wingbox_corner_points = database_connector.load_wingbox_value("wingbox_corner_points")
    left_top_corner_wingbox = wingbox_corner_points[0] * chord_length
    left_bottom_corner_wingbox = wingbox_corner_points[3] * chord_length
    right_top_corner_wingbox = wingbox_corner_points[1] * chord_length
    right_bottom_corner_wingbox = wingbox_corner_points[2] * chord_length

    length_top_plate = (math.sqrt((right_top_corner_wingbox[0] - left_top_corner_wingbox[0]) ** 2 +
                                  (left_top_corner_wingbox[1] - right_top_corner_wingbox[1]) ** 2))
    height_front_spar = (left_top_corner_wingbox[1] - left_bottom_corner_wingbox[1])
    height_back_spar = (right_top_corner_wingbox[1] - right_bottom_corner_wingbox[1])
    length_bottom_plate = (math.sqrt((right_top_corner_wingbox[0] - left_top_corner_wingbox[0]) ** 2 +
                                     (-left_bottom_corner_wingbox[1] + right_bottom_corner_wingbox[1]) ** 2))
    height_middle_spar = height_front_spar - math.sqrt((length_bottom_plate / 2) ** 2 - (length_top_plate / 2) ** 2)
    # area_wingbox = length_top_plate * height_front_spar - (length_top_plate * (height_front_spar - height_back_spar))/2

    plate_thickness = database_connector.load_wingbox_value("plate_thickness")
    spar_thickness = database_connector.load_wingbox_value("spar_thickness")

    area_front_spar = spar_thickness * height_front_spar
    area_back_spar = spar_thickness * height_back_spar
    area_middle_spar = spar_thickness * height_middle_spar
    area_top_plate = plate_thickness * length_top_plate
    area_bottom_plate = plate_thickness * length_bottom_plate

    x_top_bottom_plate = (left_top_corner_wingbox[0] + right_top_corner_wingbox[0]) * 1 / 2
    x_front_spar = left_top_corner_wingbox[0]
    x_back_spar = right_top_corner_wingbox[0]
    x_middle_spar = (left_top_corner_wingbox[0] + (right_top_corner_wingbox[0] - left_top_corner_wingbox[0]) / 2)

    z_top_plate = (left_top_corner_wingbox[1] + right_top_corner_wingbox[1]) * 1 / 2
    z_bottom_plate = (left_bottom_corner_wingbox[1] + right_bottom_corner_wingbox[1]) * 1 / 2
    z_front_spar = (left_top_corner_wingbox[1] + left_bottom_corner_wingbox[1]) * 1 / 2
    z_middle_spar = height_middle_spar / 2 + z_bottom_plate
    z_back_spar = (right_top_corner_wingbox[1] + right_bottom_corner_wingbox[1]) * 1 / 2

    # Reinforcements: stringers
    area_top_stringer = database_connector.load_wingbox_value("top_stringer_area")
    area_bottom_stringer = database_connector.load_wingbox_value("bottom_stringer_area")

    def get_x_coordinates_stringer(spanwise_location):
        # get x-coordinates stringers
        x_coordinates_stringers_top = []
        x_coordinates_stringers_bottom = []
        number_stringers_top = get_amount_of_stringers(spanwise_location, "top")
        number_stringers_bottom = get_amount_of_stringers(spanwise_location, "bottom")

        spacing_stringers_top = length_top_plate / (number_stringers_top+1)
        spacing_stringers_bottom = length_bottom_plate / (number_stringers_bottom+1)

        for number_stringer in range(1, number_stringers_top + 1):
            x_coordinate_current_stringer = left_top_corner_wingbox[0] + number_stringer * spacing_stringers_top
            x_coordinates_stringers_top.append(x_coordinate_current_stringer)
            # print(number_stringer)
        for number_stringer in range(1, number_stringers_bottom + 1):
            x_coordinate_current_stringer = left_bottom_corner_wingbox[0] + number_stringer * spacing_stringers_bottom
            x_coordinates_stringers_bottom.append(x_coordinate_current_stringer)
            # print(number_stringer)
        return x_coordinates_stringers_top, x_coordinates_stringers_bottom

    def get_z_coordinates_stringer(spanwise_location):
        z_coordinates_stringers_top = []
        z_coordinates_stringers_bottom = []

        number_stringers_top = get_amount_of_stringers(spanwise_location, "top")
        number_stringers_bottom = get_amount_of_stringers(spanwise_location, "bottom")

        spacing_stringers_top = length_top_plate / (number_stringers_top+1)
        spacing_stringers_bottom = length_bottom_plate / (number_stringers_bottom+1)

        #top
        sin_angle_top = (left_top_corner_wingbox[1] - right_top_corner_wingbox[1])/(length_top_plate)

        for number_stringer in range(1, number_stringers_top + 1):
            z_coordinate_current_top_stringer = left_top_corner_wingbox[1] - number_stringer * sin_angle_top * spacing_stringers_top
            z_coordinates_stringers_top.append(z_coordinate_current_top_stringer)
        #bottom
        sin_angle_bottom = (-left_bottom_corner_wingbox[1] - right_top_corner_wingbox[1]) / length_bottom_plate
        for number_stringer in range(1, number_stringers_bottom + 1):
            z_coordinate_current_bottom_stringer = left_bottom_corner_wingbox[1] - number_stringer * sin_angle_bottom * spacing_stringers_bottom
            z_coordinates_stringers_bottom.append(z_coordinate_current_bottom_stringer)

        # #z axis points up
        # print(z_coordinates_stringers_top)
        # print(z_coordinates_stringers_bottom)
        return z_coordinates_stringers_top,z_coordinates_stringers_bottom

    def calculate_x_coordinate_centroid(x_lst, area_lst):
        AX_lst = []
        for index in range(len(x_lst)):
            AX_lst.append(x_lst[index] * area_lst[index])
            # print(index)

        sum_area = sum(area_lst)
        sum_AX = sum(AX_lst)
        return sum_AX / sum_area

    def calculate_z_coordinate_centroid(z_lst, area_lst):
        AZ_lst = []
        for element in range(len(z_lst)):
            AZ_lst.append(z_lst[element] * area_lst[element])
        sum_area = sum(area_lst)
        sum_AZ = sum(AZ_lst)
        return sum_AZ / sum_area

    def calculate_Ixz(x_lst,z_lst,area_lst):
        IXZ_AXZ_lst = []
        for element in range(len(x_lst)):
            #print(z_lst[element])
            IXZ_AXZ_lst.append(x_lst[element] * z_lst[element] * area_lst[element])
            #print(element)
        I_XZ = sum(IXZ_AXZ_lst)
        return I_XZ


    area_lst = [area_top_plate, area_bottom_plate, area_front_spar, area_middle_spar, area_back_spar]
    x_coordinates_lst = [x_top_bottom_plate, x_top_bottom_plate, x_front_spar, x_middle_spar, x_back_spar]
    z_coordinates_lst = [z_top_plate, z_bottom_plate, z_front_spar, z_middle_spar, z_back_spar]

    # coordinates centroid without ribs and stringers (wrt LE-chord intersection)
    x_centroid_no_reinforcements = calculate_x_coordinate_centroid(x_coordinates_lst[0:5], area_lst[0:5])
    z_centroid_no_reinforcements = calculate_z_coordinate_centroid(z_coordinates_lst[0:5], area_lst[0:5])
    if verbose:
        print("\nThe centroid w.r.t. the LE-chord without any ribs or stringers equals [x,z]: ")
        print([x_centroid_no_reinforcements, z_centroid_no_reinforcements])

    # coordinates centroid with only stringers
    x_coordinates_stringers_top, x_coordinates_stringers_bottom = get_x_coordinates_stringer(spanwise_location)
    z_coordinates_stringers_top, z_coordinates_stringers_bottom = get_z_coordinates_stringer(spanwise_location)
    x_coordinates_lst = x_coordinates_lst + x_coordinates_stringers_top + x_coordinates_stringers_bottom
    z_coordinates_lst = z_coordinates_lst + z_coordinates_stringers_top + z_coordinates_stringers_bottom
    for add_area in range(len(x_coordinates_stringers_top)):
        area_lst.append(area_top_stringer)
    for add_area in range(len(x_coordinates_stringers_bottom)):
        area_lst.append(area_bottom_stringer)
    x_centroid_stringers_only = calculate_x_coordinate_centroid(x_coordinates_lst, area_lst)
    z_centroid_stringers_only = calculate_z_coordinate_centroid(z_coordinates_lst, area_lst)
    if verbose:
        print("\nThe centroid w.r.t. the LE-chord with stringers [x,z]: ")
        print([x_centroid_stringers_only, z_centroid_stringers_only])
        # print(x_coordinates_lst)
        # print(len(x_coordinates_lst))
        # print(z_coordinates_lst)
        # print(len(z_coordinates_lst))
        # print(len(area_lst))
    return [x_centroid_stringers_only, z_centroid_stringers_only]
    I_XZ = calculate_Ixz(x_coordinates_lst,z_coordinates_lst,area_lst)

    return [x_centroid_stringers_only, z_centroid_stringers_only, I_XZ]

get_centroid(1.0,verbose=True)