"""This program calculates the shear flow in the section of the wingbox with two cells"""

import numpy as np
import pickle
import scipy as sp
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
    # leading_spar_location = get_location(leading_spar)
    # trailing_spar_location = get_location(trailing_spar)
    # leading_spar_length = get_length(leading_spar)
    # trailing_spar_length = get_length(trailing_spar)
    spar_thickness = database_connector.load_wingbox_value('spar_thickness')

    top_plate_chord = [[wingbox_corner_points[0][0], wingbox_corner_points[0][1]],
                       [wingbox_corner_points[1][0], wingbox_corner_points[1][1]]]
    bottom_plate_chord = [[wingbox_corner_points[2][0], wingbox_corner_points[2][1]],
                          [wingbox_corner_points[3][0], wingbox_corner_points[3][1]]]
    top_plate = [x * aerodynamic_data.chord_function(spanwise_location) for x in top_plate_chord]
    bottom_plate = [x * aerodynamic_data.chord_function(spanwise_location) for x in bottom_plate_chord]
    # top_plate_location = get_location(top_plate)
    # bottom_plate_location = get_location(bottom_plate)
    # top_plate_length = get_length(top_plate)
    # bottom_plate_length = get_length(bottom_plate)
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

    # importing the loading data
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
    lift_lst = data[2]
    v_force = sp.interpolate.interp1d(y_span_lst, lift_lst, kind="cubic", fill_value="extrapolate")
    v_force_y = v_force(spanwise_location)

    # DRAG
    drag_lst = data[5]
    h_force = sp.interpolate.interp1d(y_span_lst, drag_lst, kind="cubic", fill_value="extrapolate")
    h_force_y = h_force(spanwise_location)

    # importing constants
    G = database_connector.load_wingbox_value("shear_modulus_pa")
    wingbox_points = database_connector.load_wingbox_value("wingbox_points")
    area_bottom_stringer = database_connector.load_wingbox_value("bottom_stringer_area")
    area_top_stringer = database_connector.load_wingbox_value("top_stringer_area")

    # thicknesses of spar and plates for torque calculations
    t_12 = t_23 = t_45 = t_56 = database_connector.load_wingbox_value("plate_thickness")
    t_34 = t_61 = t_25 = database_connector.load_wingbox_value("spar_thickness")

    # PROCESSING OF RELEVANT DATA FOR SHEAR DUE TO TORQUE CALCULATIONS
    # the 6 points are numbered from 1 to 6 from top left to bottom left in clockwise direction
    distances_1 = (wingbox_points[0][0] - centroid[0], wingbox_points[0][1] - centroid[1])
    distances_2 = (wingbox_points[1][0] - centroid[0], wingbox_points[1][1] - centroid[1])
    distances_3 = (wingbox_points[2][0] - centroid[0], wingbox_points[2][1] - centroid[1])
    distances_4 = (wingbox_points[3][0] - centroid[0], wingbox_points[3][1] - centroid[1])
    distances_5 = (wingbox_points[4][0] - centroid[0], wingbox_points[4][1] - centroid[1])
    distances_6 = (wingbox_points[5][0] - centroid[0], wingbox_points[5][1] - centroid[1])

    chord_length = aerodynamic_data.chord_function(spanwise_location)

    length_12 = abs(distances_1[0] - distances_2[0]) * chord_length
    length_23 = abs(distances_2[0] - distances_3[0]) * chord_length
    length_34 = abs(distances_3[1] - distances_4[1]) * chord_length
    # length_45 = abs(distances_4[0] - distances_5[0]) * chord_length
    # length_56 = abs(distances_5[0] - distances_6[0]) * chord_length
    length_61 = abs(distances_6[1] - distances_1[1]) * chord_length
    length_25 = abs(distances_2[1] - distances_5[1]) * chord_length

    encl_area_1256 = (length_25 + length_61) * length_12 / 2
    encl_area_2345 = (length_25 + length_34) * length_23 / 2

    # PROCESSING OF RELEVANT DATA FOR SHEAR DUE TO VERTICAL FORCE CALCULATIONS
    # q_b calculations for each boom
    MoI_xx = area_top_stringer * (distances_1[1] ** 2 + distances_2[1] ** 2 + distances_3[1] ** 2) \
             + area_bottom_stringer * (distances_4[1] ** 2 + distances_5[1] ** 2 + distances_6[1] ** 2)
    MoI_yy = area_top_stringer * (distances_1[0] ** 2 + distances_2[0] ** 2 + distances_3[0] ** 2) \
             + area_bottom_stringer * (distances_4[0] ** 2 + distances_5[0] ** 2 + distances_6[0] ** 2)

    # The integral term for Lorezno
    def q_b(distance_from_centroid, area):
        return - (MoI_xx * h_force_y) / (MoI_xx * MoI_yy) * (area * distance_from_centroid[0]) - \
               (MoI_yy * v_force_y) / (MoI_xx * MoI_yy) * (area * distance_from_centroid[1])

    # BOTTOM FLANGES q_b
    # q_b for the first cell (two flanges)
    q_b_16 = q_b(distances_1, area_top_stringer)

    integral_value_front_bottom = q_b_16
    q_b_lst_bottom_surface_frontcell = []
    # Bottom stringers of front cell (Change as you see fit Lorezno)
    for stringer_index in range(0, int(round(len(stringer_bottom_distance_from_centroid) / 2))):
        integral_value_front_bottom += (q_b(stringer_bottom_distance_from_centroid[stringer_index],
                                            area_bottom_stringer) *
                                        get_length([stringer_bottom_locations[stringer_index],
                                                    stringer_bottom_locations[stringer_index - 1]])) / (
                                               plate_thickness * G)
        q_b_lst_bottom_surface_frontcell.append(integral_value_front_bottom)

    # q_b for the second cell (two flanges)
    q_b_25 = q_b(distances_2, area_top_stringer)
    integral_value_aft_bottom = q_b_25
    q_b_lst_bottom_surface_aftcell = []
    # Bottom stringers of aft cell (Change as you see fit)
    for stringer_index in range(int(round(len(stringer_bottom_distance_from_centroid) / 2)),
                                int(round(len(stringer_bottom_distance_from_centroid)))):
        integral_value_aft_bottom += (q_b(stringer_bottom_distance_from_centroid[stringer_index],
                                          area_bottom_stringer) *
                                      get_length([stringer_bottom_locations[stringer_index],
                                                  stringer_bottom_locations[stringer_index - 1]])) / (
                                             plate_thickness * G)
        q_b_lst_bottom_surface_aftcell.append(integral_value_aft_bottom)

    # TOP FLANGES q_b
    integral_value_front_top = q_b_lst_bottom_surface_frontcell[-1]
    q_b_lst_top_surface_frontcell = []
    # Bottom stringers of front cell (Change as you see fit Lorezno)
    for stringer_index in range(0, int(round(len(stringer_top_distance_from_centroid) / 2))):
        integral_value_front_top += (q_b(stringer_top_distance_from_centroid[stringer_index], area_top_stringer) *
                                     get_length([stringer_top_locations[stringer_index],
                                                 stringer_top_locations[stringer_index - 1]])) / (plate_thickness * G)
        q_b_lst_bottom_surface_frontcell.append(integral_value_front_top)

    # q_b for the second cell (two flanges)
    integral_value_aft_top = q_b_lst_bottom_surface_aftcell[-1]
    q_b_lst_top_surface_aftcell = []
    # Bottom stringers of aft cell (Change as you see fit)
    for stringer_index in range(int(round(len(stringer_top_distance_from_centroid) / 2)),
                                int(round(len(stringer_top_distance_from_centroid)))):
        integral_value_aft_top += (q_b(stringer_top_distance_from_centroid[stringer_index], area_top_stringer) *
                                   get_length([stringer_top_locations[stringer_index],
                                               stringer_top_locations[stringer_index - 1]])) / (plate_thickness * G)
        q_b_lst_top_surface_aftcell.append(integral_value_aft_top)

    inter_stringer_distance_bottom = abs(
        stringer_bottom_distance_from_centroid[0] - stringer_bottom_distance_from_centroid[1])
    inter_stringer_distance_top = abs(
        stringer_top_distance_from_centroid[0] - stringer_top_distance_from_centroid[1])

    p1 = np.array([centroid[0], centroid[1]])
    p2 = np.array(stringer_bottom_distance_from_centroid[0])
    p3 = np.array(stringer_bottom_distance_from_centroid[1])
    moment_arm_bottom_surface_qbs = np.cross(p2 - p1, p3 - p1) / np.linalg.norm(p2 - p1)

    # moment generated by qbs and forces around point 2

    ## TO BE CHECKED WITH RASA
    moment_due_to_forces = v_force_y * distances_2[0] + h_force_y * distances_2[1]

    ## Direction to be checked
    moment_due_to_bottom_surface_qbs_frontcell = integral_value_front_bottom * \
                                                 length_12 \
                                                 + moment_arm_bottom_surface_qbs * \
                                                 sum(q_b_lst_bottom_surface_frontcell[:-1])
    moment_due_to_bottom_surface_qbs_aftcell = moment_arm_bottom_surface_qbs * \
                                               sum(q_b_lst_bottom_surface_aftcell[:-1]) + \
                                               length_34 * \
                                               q_b_lst_bottom_surface_aftcell[-1]

    total_moment_forces_qbs_allcell = moment_due_to_forces - moment_due_to_bottom_surface_qbs_frontcell - \
                                      moment_due_to_bottom_surface_qbs_aftcell

    # line integrals functional to the equation with dthetha/dz
    # bottom plates
    line_integral_qb_frontcell_bottom = (integral_value_front_bottom * length_61 + q_b_lst_bottom_surface_frontcell[
        -1] *
                                         length_25) / (t_61 * G)
    for element in q_b_lst_bottom_surface_frontcell[:-1]:
        line_integral_qb_frontcell_bottom += element * inter_stringer_distance_bottom / (t_56 * G)
    line_integral_qb_aftcell_bottom = (integral_value_aft_bottom * length_25 + q_b_lst_bottom_surface_aftcell[-1]
                                       * length_34) / (t_25 * G)
    for element in q_b_lst_bottom_surface_aftcell[:-1]:
        line_integral_qb_aftcell_bottom += element * inter_stringer_distance_bottom / (t_45 * G)
        # top plates
    line_integral_qb_frontcell_top = 0
    for element in q_b_lst_top_surface_frontcell[:-1]:
        line_integral_qb_frontcell_top += element * inter_stringer_distance_top / (t_12 * G)
    line_integral_qb_aftcell_top = 0
    for element in q_b_lst_top_surface_aftcell[:-1]:
        line_integral_qb_aftcell_top += element * inter_stringer_distance_top / (t_23 * G)

    dthetha_dz_contribution_qb_frontcell = (line_integral_qb_frontcell_bottom + line_integral_qb_frontcell_bottom) \
                                           / (2 * encl_area_1256)
    dthetha_dz_contribution_qb_aftcell = (line_integral_qb_aftcell_bottom + line_integral_qb_aftcell_top) \
                                         / (2 * encl_area_1256)

    # Matrix
    matrix = np.array([[2 * encl_area_1256, 2 * encl_area_2345, 0],
                       [1 / (2 * encl_area_1256 * G) * (1 / t_12 + 1 / t_61 + 1 / t_25 + 1 / t_56),
                        1 / (2 * encl_area_1256 * G) * (- 1 / t_25), -1],
                       [1 / (2 * encl_area_2345 * G) * (- 1 / t_25),
                        1 / (2 * encl_area_2345 * G) * (1 / t_23 + 1 / t_34 + 1 / t_45 + 1 / t_25), -1]])

    # SHEAR DUE TO TORQUE
    solution_vector_t = np.array([0, 0, torque_y])
    q_t_1256, q_t_2345, dtheta_t = np.linalg.solve(matrix, solution_vector_t)

    # SHEAR DUE TO VERTICAL and HORIZONTAL FORCE #tbf
    solution_vector_s = np.array([total_moment_forces_qbs_allcell, dthetha_dz_contribution_qb_frontcell,
                                  dthetha_dz_contribution_qb_aftcell])
    q_s_s0_1256, q_s_s0_2345, dtheta_s = np.linalg.solve(matrix, solution_vector_s)

    # TOTAL SHEAR FORCE EVALUATION IN EACH SECTION
    q_max_top_flange_value_position = [0, (0, 0)]
    q_max_bottom_flange_value_position = [0, (0, 0)]

    # top surface
    for q_b in q_b_lst_top_surface_aftcell:
        q_tot = q_t_1256 + q_s_s0_1256 + q_b
        if abs(q_tot) > q_max_top_flange_value_position[0]:
            q_max_top_flange_value_position[0] = q_tot, q_max_top_flange_value_position[1] = (x, y_top_plate)

    # bottom surface
    for x in reinir_list:
        q_tot = q_t_1256 + q_s_s0_1256 + q_b_from_reinir[x]
        if abs(q_tot) > q_max_bottom_flange_value_position[0]:
            q_max_bottom_flange_value_position[0] = q_tot, q_max_bottom_flange_value_position[1] = (x, y_bottom_plate)

    # flanges
    for x in reinir_list:
        q_tot = q_t_1256 + q_s_s0_1256 + q_b_from_reinir[x]

    return
