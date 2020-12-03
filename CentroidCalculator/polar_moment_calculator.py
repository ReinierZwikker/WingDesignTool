import numpy as np

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

wing_surface_area = database_connector.load_value("surface_area")


def centroid_placeholder(spanwise_location):
    return tuple([0.5, 0.5])


def get_amount_of_stringers(spanwise_location, top):
    amount_of_stringers = 0
    if top:
        if spanwise_location < database_connector.load_wingbox_value('top_stringer_lim_point_1'):
            amount_of_stringers += database_connector.load_wingbox_value('top_number_of_stringers_1')
        elif spanwise_location < database_connector.load_wingbox_value('top_stringer_lim_point_2'):
            amount_of_stringers += database_connector.load_wingbox_value('top_number_of_stringers_2')
        else:
            amount_of_stringers += database_connector.load_wingbox_value('top_number_of_stringers_3')
    if not top:
        if spanwise_location < database_connector.load_wingbox_value('bottom_stringer_lim_point_1'):
            amount_of_stringers += database_connector.load_wingbox_value('bottom_number_of_stringers_1')
        elif spanwise_location < database_connector.load_wingbox_value('bottom_stringer_lim_point_2'):
            amount_of_stringers += database_connector.load_wingbox_value('bottom_number_of_stringers_2')
        else:
            amount_of_stringers += database_connector.load_wingbox_value('bottom_number_of_stringers_3')
    if spanwise_location < 10:
        amount_of_stringers += 4
    else:
        amount_of_stringers += 2
    return amount_of_stringers


def get_polar_moment_of_inertia(spanwise_location):
    """
    Calculates the polar moment of inertia of the wingbox around the centroid.
    It uses a combination of rect subdivision and boom approximation to find this moment.

    :param spanwise_location: The location of the cross-section along the span for which the polar moment of Inertia is calculated.
    :return: The polar moment of Inertia of the wingbox cross-section in m4
    """

    # Local coord system: x from LE to TE, y upwards

    centroid = centroid_placeholder(spanwise_location)

    wingbox_corner_points = database_connector.load_wingbox_value('wingbox_corner_points')

    # Get all plate dimensions by rearranging corner points
    leading_spar_chord = [[wingbox_corner_points[0][0], wingbox_corner_points[0][1]], [wingbox_corner_points[3][0], wingbox_corner_points[3][1]]]
    trailing_spar_chord = [[wingbox_corner_points[1][0], wingbox_corner_points[1][1]], [wingbox_corner_points[2][0], wingbox_corner_points[2][1]]]
    leading_spar = [x * aerodynamic_data.chord_function(spanwise_location) for x in leading_spar_chord]
    trailing_spar = [x * aerodynamic_data.chord_function(spanwise_location) for x in trailing_spar_chord]
    leading_spar_location = [(leading_spar[0][0] + leading_spar[1][0])/2, (leading_spar[0][1] + leading_spar[1][1])/2]
    trailing_spar_location = [(trailing_spar[0][0] + trailing_spar[1][0])/2, (trailing_spar[0][1] + trailing_spar[1][1])/2]
    spar_thickness = database_connector.load_wingbox_value('spar_thickness')

    print(leading_spar_chord)
    print(leading_spar)

    top_plate_chord = [[wingbox_corner_points[0][0], wingbox_corner_points[0][1]], [wingbox_corner_points[1][0], wingbox_corner_points[1][1]]]
    bottom_plate_chord = [[wingbox_corner_points[2][0], wingbox_corner_points[2][1]], [wingbox_corner_points[3][0], wingbox_corner_points[3][1]]]
    top_plate = [x * aerodynamic_data.chord_function(spanwise_location) for x in top_plate_chord]
    bottom_plate = [x * aerodynamic_data.chord_function(spanwise_location) for x in bottom_plate_chord]
    top_plate_location = [(top_plate[0][0] + top_plate[1][0])/2, (top_plate[0][1] + top_plate[1][1])/2]
    bottom_plate_location = [(bottom_plate[0][0] + bottom_plate[1][0])/2, (bottom_plate[0][1] + bottom_plate[1][1])/2]
    plate_thickness = database_connector.load_wingbox_value('plate_thickness')

    # Get stringer locations along the top and bottom plate:
    stringer_top_locations = np.linspace(top_plate[0][0], top_plate[1][0], get_amount_of_stringers(spanwise_location, True))
    stringer_bottom_locations = np.linspace(bottom_plate[0][0], bottom_plate[1][0], get_amount_of_stringers(spanwise_location, False))

    print(top_plate[0][0], top_plate[1][0])
    print(get_amount_of_stringers(spanwise_location, True), get_amount_of_stringers(spanwise_location, False))
    print(stringer_top_locations, '\n\n', stringer_bottom_locations)

    def ll_axis_term(Area, location):
        return Area * (location[0]**2+location[1]**2)

    def p_moi_rect(height, width, location):
        pass

    def p_moi_point(area, location):
        pass


get_polar_moment_of_inertia(1)