"""This program calculates the shear flow in the section of the wingbox with two cells"""

import numpy as np
import pickle
import scipy as sp

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


def shearflow_doublecell(spanwise_location):
    centroid = get_centroid(spanwise_location)

    # PROGRAM FROM REINIR TO GET STRINGER LOCATIONS
    wingbox_corner_points = database_connector.load_wingbox_value('wingbox_corner_points')

    def get_location(end_points):
        # Input end_points as [[x1,y1], [x2,y2]]
        return [(end_points[0][0] + end_points[1][0]) / 2 - centroid[0],
                (end_points[0][1] + end_points[1][1]) / 2 - centroid[1]]

    def get_length(end_points):
        # Input end_points as [[x1,y1], [x2,y2]]
        return ((end_points[0][0] - end_points[1][0]) ** 2 + (end_points[0][1] - end_points[1][1]) ** 2) ** 0.5

    # Get all plate dimensions by rearranging corner points
    leading_spar_chord = [[wingbox_corner_points[0][0], wingbox_corner_points[0][1]],
                          [wingbox_corner_points[3][0], wingbox_corner_points[3][1]]]
    trailing_spar_chord = [[wingbox_corner_points[1][0], wingbox_corner_points[1][1]],
                           [wingbox_corner_points[2][0], wingbox_corner_points[2][1]]]
    leading_spar = [x * aerodynamic_data.chord_function(spanwise_location) for x in leading_spar_chord]
    trailing_spar = [x * aerodynamic_data.chord_function(spanwise_location) for x in trailing_spar_chord]
    leading_spar_location = get_location(leading_spar)
    trailing_spar_location = get_location(trailing_spar)
    leading_spar_length = get_length(leading_spar)
    trailing_spar_length = get_length(trailing_spar)
    spar_thickness = database_connector.load_wingbox_value('spar_thickness')

    top_plate_chord = [[wingbox_corner_points[0][0], wingbox_corner_points[0][1]],
                       [wingbox_corner_points[1][0], wingbox_corner_points[1][1]]]
    bottom_plate_chord = [[wingbox_corner_points[2][0], wingbox_corner_points[2][1]],
                          [wingbox_corner_points[3][0], wingbox_corner_points[3][1]]]
    top_plate = [x * aerodynamic_data.chord_function(spanwise_location) for x in top_plate_chord]
    bottom_plate = [x * aerodynamic_data.chord_function(spanwise_location) for x in bottom_plate_chord]
    top_plate_location = get_location(top_plate)
    bottom_plate_location = get_location(bottom_plate)
    top_plate_length = get_length(top_plate)
    bottom_plate_length = get_length(bottom_plate)
    plate_thickness = database_connector.load_wingbox_value('plate_thickness')

    # Get stringer locations along the top and bottom plate:
    stringer_top_locations = np.transpose(
        [np.linspace(top_plate[0][0], top_plate[1][0], get_amount_of_stringers(spanwise_location, True)),
         np.linspace(top_plate[0][1], top_plate[1][1], get_amount_of_stringers(spanwise_location, True))])
    stringer_top_distance_from_centroid = stringer_top_locations - centroid
    stringer_bottom_locations = np.transpose(
        [np.linspace(bottom_plate[0][0], bottom_plate[1][0], get_amount_of_stringers(spanwise_location, False)),
         np.linspace(bottom_plate[0][1], bottom_plate[1][1], get_amount_of_stringers(spanwise_location, False))])
    stringer_bottom_distance_from_centroid = stringer_bottom_locations - centroid

    # END OF PROGRAM FROM REINIER

    # importing the torque data
    try:
        with open("./data.pickle", 'rb') as file:
            data = pickle.load(file)
    except FileNotFoundError:
        with open("../InertialLoadingCalculator/data.pickle", 'rb') as file:
            data = pickle.load(file)
    y_span_lst = data[0]

    # TORQUE
    torsion_lst = data[7]
    torsion = sp.interpolate.interp1d(y_span_lst, torsion_lst, kind="cubic", fill_value="extrapolate")
    torque_y = torsion(spanwise_location)

    # positive z is downwards
    # LIFT
    lift_lst = data[5]
    v_force = sp.interpolate.interp1d(y_span_lst, lift_lst, kind="cubic", fill_value="extrapolate")
    v_force_y = v_force(spanwise_location)

    # DRAG
    drag_lst = data[4]
    h_force = sp.interpolate.interp1d(y_span_lst, drag_lst, kind="cubic", fill_value="extrapolate")
    h_force_y = h_force(spanwise_location)

    # importing data
    G = database_connector.load_wingbox_value("shear_modulus_pa")

    t_12 = database_connector.load_wingbox_value("plate_thickness")
    t_23 = database_connector.load_wingbox_value("plate_thickness")
    t_34 = database_connector.load_wingbox_value("spar_thickness")
    t_45 = database_connector.load_wingbox_value("plate_thickness")
    t_56 = database_connector.load_wingbox_value("plate_thickness")
    t_61 = database_connector.load_wingbox_value("spar_thickness")
    t_25 = database_connector.load_wingbox_value("spar_thickness")

    wingbox_points = database_connector.load_wingbox_value("wingbox_points")

    area_top_stringer = database_connector.load_wingbox_value("top_stringer_area")
    area_bottom_stringer = database_connector.load_wingbox_value("bottom_stringer_area")
    #
    # # PROCESSING OF RELEVANT DATA
    # the 6 points are numbered from 1 to 6 from top left to bottom left in clockwise direction
    wingbox_points = database_connector.load_wingbox_value("wingbox_points")
    distances_1 = (wingbox_points[0][0] - centroid[0], wingbox_points[0][1] - centroid[1])
    distances_2 = (wingbox_points[1][0] - centroid[0], wingbox_points[1][1] - centroid[1])
    distances_3 = (wingbox_points[2][0] - centroid[0], wingbox_points[2][1] - centroid[1])
    distances_4 = (wingbox_points[3][0] - centroid[0], wingbox_points[3][1] - centroid[1])
    distances_5 = (wingbox_points[4][0] - centroid[0], wingbox_points[4][1] - centroid[1])
    distances_6 = (wingbox_points[5][0] - centroid[0], wingbox_points[5][1] - centroid[1])

    chord_length = aerodynamic_data.chord_function(spanwise_location)
    #
    length_12 = abs(distances_1[0] - distances_2[0]) * chord_length
    length_23 = abs(distances_2[0] - distances_3[0]) * chord_length
    length_34 = abs(distances_3[1] - distances_4[1]) * chord_length
    # length_45 = abs(distances_4[0] - distances_5[0]) * chord_length
    # length_56 = abs(distances_5[0] - distances_6[0]) * chord_length
    length_61 = abs(distances_6[1] - distances_1[1]) * chord_length
    length_25 = abs(distances_2[1] - distances_5[1]) * chord_length

    encl_area_1256 = (length_25 + length_61) * length_12 / 2
    encl_area_2345 = (length_25 + length_34) * length_23 / 2

    # Delta q_b calculations for each boom
    MoI_xx = area_top_stringer * (distances_1[1] ** 2 + distances_2[1] ** 2 + distances_3[1] ** 2) \
             + area_bottom_stringer * (distances_4[1] ** 2 + distances_5[1] ** 2 + distances_6[1] ** 2)
    MoI_yy = area_top_stringer * (distances_1[0] ** 2 + distances_2[0] ** 2 + distances_3[0] ** 2) \
             + area_bottom_stringer * (distances_4[0] ** 2 + distances_5[0] ** 2 + distances_6[0] ** 2)

    Delta_q_1 = - h_force_y / MoI_yy * area_top_stringer * distances_1[0] \
                - v_force_y / MoI_xx * area_top_stringer * distances_1[1]
    Delta_q_2 = - h_force_y / MoI_yy * area_top_stringer * distances_2[0] \
                - v_force_y / MoI_xx * area_top_stringer * distances_2[1]
    Delta_q_3 = - h_force_y / MoI_yy * area_top_stringer * distances_3[0] \
                - v_force_y / MoI_xx * area_top_stringer * distances_3[1]
    Delta_q_4 = - h_force_y / MoI_yy * area_top_stringer * distances_4[0] \
                - v_force_y / MoI_xx * area_top_stringer * distances_4[1]
    Delta_q_5 = - h_force_y / MoI_yy * area_top_stringer * distances_5[0] \
                - v_force_y / MoI_xx * area_top_stringer * distances_5[1]
    Delta_q_6 = - h_force_y / MoI_yy * area_top_stringer * distances_6[0] \
                - v_force_y / MoI_xx * area_top_stringer * distances_6[1]

    # The integral term for Lorenzo
    def q_b(distance_from_centroid, area):
        return - (MoI_xx * h_force_y) / (MoI_xx * MoI_yy) * (area * distance_from_centroid[0]) - \
               (MoI_yy * v_force_y) / (MoI_xx * MoI_yy) * (area * distance_from_centroid[1])

    integral_value_front = 0
    # Bottom stringers of front cell (Change as you see fit lorezno)
    for stringer_index in range(0, int(round(len(stringer_bottom_distance_from_centroid) / 2))):
        integral_value_front += (q_b(stringer_bottom_distance_from_centroid[stringer_index], area_bottom_stringer) *
                                 get_length([stringer_bottom_locations[stringer_index], stringer_bottom_locations[stringer_index - 1]])) / (plate_thickness * G)

    integral_value_aft = 0
    # Bottom stringers of aft cell (Change as you see fit)
    for stringer_index in range(int(round(len(stringer_bottom_distance_from_centroid) / 2)), int(round(len(stringer_bottom_distance_from_centroid)))):
        integral_value_aft += (q_b(stringer_bottom_distance_from_centroid[stringer_index], area_bottom_stringer) *
                               get_length([stringer_bottom_locations[stringer_index], stringer_bottom_locations[stringer_index - 1]])) / (plate_thickness * G)

    print(integral_value_front, integral_value_aft)

    # Matrix
    matrix = np.array([[2 * encl_area_1256, 2 * encl_area_2345, 0],
                       [1 / (2 * encl_area_1256 * G) * (1 / t_12 + 1 / t_61 + 1 / t_25 + 1 / t_56),
                        1 / (2 * encl_area_1256 * G) * (- 1 / t_25), -1],
                       [1 / (2 * encl_area_2345 * G) * (- 1 / t_25),
                        1 / (2 * encl_area_2345 * G) * (1 / t_23 + 1 / t_34 + 1 / t_45 + 1 / t_25), -1]])

    # SHEAR DUE TO TORQUE
    solution_vector_t = np.array([0, 0, torque_y])
    q_t_1256, q_t_2345, dtheta_t = np.linalg.solve(matrix, solution_vector_t)

    # SHEAR DUE TO VERTICAL FORCE #tbf
    solution_vector_s = np.array([0, 0, 0])
    q_t_1256, q_t_2345, dtheta_s = np.linalg.solve(matrix, solution_vector_s)

    return


shearflow_doublecell(8)
