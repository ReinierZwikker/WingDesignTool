import numpy as np

try:
    from Database.database_functions import DatabaseConnector
    from CentroidCalculator.centroid_funcs import get_amount_of_stringers
    from CentroidCalculator.centroid_calculator import get_centroid
    import Importer.xflr5 as aerodynamic_data
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    from CentroidCalculator.centroid_funcs import get_amount_of_stringers
    from CentroidCalculator.centroid_calculator import get_centroid
    import Importer.xflr5 as aerodynamic_data

database_connector = DatabaseConnector()


def get_polar_moment_of_inertia(spanwise_location):
    """
    Calculates the polar moment of inertia of the wingbox around the centroid.
    It uses a combination of rect subdivision and boom approximation to find this moment.

    :param spanwise_location: The location of the cross-section along the span for which the polar moment of Inertia is calculated.
    :return: The polar moment of Inertia of the wingbox cross-section in m4
    """

    # Local coord system: x from LE to TE, y upwards

    centroid = get_centroid(spanwise_location)

    top_stringer_area = database_connector.load_wingbox_value('top_stringer_area')
    bottom_stringer_area = database_connector.load_wingbox_value('bottom_stringer_area')

    wingbox_corner_points = database_connector.load_wingbox_value('wingbox_corner_points')

    def get_location(end_points):
        # Input end_points as [[x1,y1], [x2,y2]]
        return [(end_points[0][0] + end_points[1][0]) / 2 - centroid[0], (end_points[0][1] + end_points[1][1]) / 2 - centroid[1]]

    def get_length(end_points):
        # Input end_points as [[x1,y1], [x2,y2]]
        return ((end_points[0][0] - end_points[1][0])**2 + (end_points[0][1] - end_points[1][1])**2)**0.5

    # Get all plate dimensions by rearranging corner points
    leading_spar_chord = [[wingbox_corner_points[0][0], wingbox_corner_points[0][1]], [wingbox_corner_points[3][0], wingbox_corner_points[3][1]]]
    trailing_spar_chord = [[wingbox_corner_points[1][0], wingbox_corner_points[1][1]], [wingbox_corner_points[2][0], wingbox_corner_points[2][1]]]
    leading_spar = [x * aerodynamic_data.chord_function(spanwise_location) for x in leading_spar_chord]
    trailing_spar = [x * aerodynamic_data.chord_function(spanwise_location) for x in trailing_spar_chord]
    leading_spar_location = get_location(leading_spar)
    trailing_spar_location = get_location(trailing_spar)
    leading_spar_length = get_length(leading_spar)
    trailing_spar_length = get_length(trailing_spar)
    spar_thickness = database_connector.load_wingbox_value('spar_thickness')

    top_plate_chord = [[wingbox_corner_points[0][0], wingbox_corner_points[0][1]], [wingbox_corner_points[1][0], wingbox_corner_points[1][1]]]
    bottom_plate_chord = [[wingbox_corner_points[2][0], wingbox_corner_points[2][1]], [wingbox_corner_points[3][0], wingbox_corner_points[3][1]]]
    top_plate = [x * aerodynamic_data.chord_function(spanwise_location) for x in top_plate_chord]
    bottom_plate = [x * aerodynamic_data.chord_function(spanwise_location) for x in bottom_plate_chord]
    top_plate_location = get_location(top_plate)
    bottom_plate_location = get_location(bottom_plate)
    top_plate_length = get_length(top_plate)
    bottom_plate_length = get_length(bottom_plate)
    plate_thickness = database_connector.load_wingbox_value('plate_thickness')

    # Get stringer locations along the top and bottom plate:
    stringer_top_locations = np.transpose([np.linspace(top_plate[0][0], top_plate[1][0], get_amount_of_stringers(spanwise_location, True)),
                                           np.linspace(top_plate[0][1], top_plate[1][1], get_amount_of_stringers(spanwise_location, True))])
    stringer_bottom_locations = np.transpose([np.linspace(bottom_plate[0][0], bottom_plate[1][0], get_amount_of_stringers(spanwise_location, False)),
                                              np.linspace(bottom_plate[0][1], bottom_plate[1][1], get_amount_of_stringers(spanwise_location, False))])

    def ll_axis_term(Area, location):
        # parallel axis term
        return Area * (location[0]**2+location[1]**2)

    def p_moi_rect(height, width, location):
        # Standard formula and parallel axis term
        return (width * height * (width**2 + height**2)) / 12 + ll_axis_term(width * height, location)

    def p_moi_point(area, location):
        # Treat as point area and neglect terms except for parallel axis term
        return 0 + ll_axis_term(area, location)

    polar_moment_of_inertia = 0

    # Due to plates
    polar_moment_of_inertia += p_moi_rect(leading_spar_length, spar_thickness, leading_spar_location)
    polar_moment_of_inertia += p_moi_rect(trailing_spar_length, spar_thickness, trailing_spar_location)
    polar_moment_of_inertia += p_moi_rect(plate_thickness, top_plate_length, top_plate_location)
    polar_moment_of_inertia += p_moi_rect(plate_thickness, bottom_plate_length, bottom_plate_location)

    # Due to top stringers
    for stringer_location in stringer_top_locations:
        polar_moment_of_inertia += p_moi_point(top_stringer_area, stringer_location)

    # Due to bottom stringers
    for stringer_location in stringer_bottom_locations:
        polar_moment_of_inertia += p_moi_point(bottom_stringer_area, stringer_location)

    return polar_moment_of_inertia


print(get_polar_moment_of_inertia(26))
