import pickle
import matplotlib.pyplot as plt

try:
    from Database.database_functions import DatabaseConnector
    from Buckling.stringer_applied import string_stress_normal
    from Buckling.stringer_crit import crit_stress_stringer
    from Buckling.shear_flow_multicell import shearflow_doublecell
    from Buckling.plate_crit import plate_crit_force
    from Buckling.spar_crit import spar_crit_stress
    from Buckling.Shear_flow_1cell import main_shear_stress
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    from Buckling.stringer_applied import string_stress_normal, string_stress_tension
    from Buckling.stringer_crit import crit_stress_stringer
    from Buckling.shear_flow_multicell import shearflow_doublecell
    from Buckling.plate_crit import plate_crit_force
    from Buckling.spar_crit import spar_crit_stress
    from Buckling.Shear_flow_1cell import main_shear_stress

database_connector = DatabaseConnector()

try:
    with open("../InertialLoadingCalculator/data.pickle", 'rb') as file:
        data = pickle.load(file)
except FileNotFoundError:
    with open("./data.pickle", 'rb') as file:
        data = pickle.load(file)

y_lst = data[0][:-60]
strength = database_connector.load_wingbox_value("ultimate_strength")
crack_strength = 231400000
shear_strength = database_connector.load_wingbox_value('shear_strength')

def margin_safety_crit(applied, crit):
    factor = crit/applied
    return factor

def margin_safety_strength(applied):
    factor = strength/applied
    return factor

def plot(mode='compression'):
    """"
    mode can be compression, for the buckling diagrams
    or tension for the tension strength diagrams
    """
    margin_stringer_crit = []
    margin_stringer_strength = []
    margin_stringer = []
    tension_stress = []
    stress_crack = []
    margin_crack = []
    mos_plate_strength = []
    mos_plate_crit = []
    mos_plate = []
    mos_spar_strength = []
    mos_spar_crit = []
    mos_spar = []
    for y in y_lst:
        if mode == 'top_plate':
            if y < 10:
                mos_plate_strength.append(margin_safety_crit(shearflow_doublecell(y)[0], shear_strength))
                mos_plate_crit.append(margin_safety_crit(shearflow_doublecell(y)[0], plate_crit_force(y, mode="top")))
                mos_plate.append(min(mos_plate_strength[-1], mos_plate_crit[-1]))
            if y > 10:
                mos_plate_strength.append(margin_safety_crit(main_shear_stress(y)[1], shear_strength))
                mos_plate_crit.append(margin_safety_crit(main_shear_stress(y)[1], plate_crit_force(y, mode="top")))
                mos_plate.append(min(mos_plate_strength[-1], mos_plate_crit[-1]))
        if mode == 'bottom_plate':
            if y < 10:
                mos_plate_strength.append(margin_safety_crit(shearflow_doublecell(y)[1], shear_strength))
                mos_plate_crit.append(margin_safety_crit(shearflow_doublecell(y)[1], plate_crit_force(y, mode="bottom")))
                mos_plate.append(min(mos_plate_strength[-1], mos_plate_crit[-1]))
            if y > 10:
                mos_plate_strength.append(margin_safety_crit(main_shear_stress(y)[0], shear_strength))
                mos_plate_crit.append(margin_safety_crit(main_shear_stress(y)[0], plate_crit_force(y, mode="bottom")))
                mos_plate.append(min(mos_plate_strength[-1], mos_plate_crit[-1]))
        if mode == 'spar':
            if y < 10:
                mos_spar_strength.append(margin_safety_crit(shearflow_doublecell(y)[2], shear_strength))
                mos_spar_crit.append(margin_safety_crit(shearflow_doublecell(y)[2], spar_crit_stress(y)))
                mos_spar.append(min(mos_spar_strength[-1], mos_spar_crit[-1]))
            if y > 10:
                mos_spar_strength.append(margin_safety_crit(main_shear_stress(y)[2], shear_strength))
                mos_spar_crit.append(margin_safety_crit(main_shear_stress(y)[2], spar_crit_stress(y)))
                mos_spar.append(min(mos_spar_strength[-1], mos_spar_crit[-1]))

        if mode == 'stringer':
            margin_stringer_crit.append(margin_safety_crit(string_stress_normal(y), crit_stress_stringer(y)))
            margin_stringer_strength.append(margin_safety_strength(string_stress_normal(y)))
            margin_stringer.append(min(margin_stringer_crit[-1], margin_stringer_strength[-1]))
       
        if mode == 'tension':
            margin_stringer_strength.append(margin_safety_strength(string_stress_tension(y)))
            tension_stress.append(string_stress_tension(y))

        
        if mode == 'crack':
            stress_crack.append(string_stress_tension(y))
            margin_crack.append(margin_safety_crit(string_stress_tension(y), crack_strength))
    
    if mode == 'top_plate':
        plt.figure()
        plt.suptitle('Margin of safety for the top plate with regards to shear', y=0.99)

        plt.subplot(311)
        plt.title('Buckling margin of safety', y=1)
        plt.plot(y_lst, mos_plate_crit)
        plt.xlabel("Spanwise location on the wing (m)")
        plt.ylabel('Margin of safety')
        plt.subplots_adjust(top=0.95, bottom=0.05)

        plt.subplot(312)
        plt.title('Strength margin of safety', y=1)
        plt.plot(y_lst, mos_plate_strength)
        plt.xlabel("Spanwise location on the wing (m)")
        plt.ylabel('Margin of safety')

        plt.subplot(313)
        plt.title('Combined margin of safety', y=1)
        plt.plot(y_lst, mos_plate)
        plt.xlabel("Spanwise location on the wing (m)")
        plt.ylabel('Margin of safety')
    if mode == 'bottom_plate':
        plt.figure()
        plt.suptitle('Margin of safety for the bottom plate with regards to shear', y=0.99)

        plt.subplot(311)
        plt.title('Buckling margin of safety', y=1)
        plt.plot(y_lst, mos_plate_crit)
        plt.xlabel("Spanwise location on the wing (m)")
        plt.ylabel('Margin of safety')
        plt.subplots_adjust(top=0.95, bottom=0.05)

        plt.subplot(312)
        plt.title('Strength margin of safety', y=1)
        plt.plot(y_lst, mos_plate_strength)
        plt.xlabel("Spanwise location on the wing (m)")
        plt.ylabel('Margin of safety')

        plt.subplot(313)
        plt.title('Combined margin of safety', y=1)
        plt.plot(y_lst, mos_plate)
        plt.xlabel("Spanwise location on the wing (m)")
        plt.ylabel('Margin of safety')
    if mode == 'spar':
        plt.figure()
        plt.suptitle('Margin of safety for the spars with regards to shear', y=0.99)

        plt.subplot(311)
        plt.title('Buckling margin of safety', y=1)
        plt.plot(y_lst, mos_spar_crit)
        plt.xlabel("Spanwise location on the wing (m)")
        plt.ylabel('Margin of safety')
        plt.subplots_adjust(top=0.95, bottom=0.05)

        plt.subplot(312)
        plt.title('Strength margin of safety', y=1)
        plt.plot(y_lst, mos_spar_strength)
        plt.xlabel("Spanwise location on the wing (m)")
        plt.ylabel('Margin of safety')

        plt.subplot(313)
        plt.title('Combined margin of safety', y=1)
        plt.plot(y_lst, mos_spar)
        plt.xlabel("Spanwise location on the wing (m)")
        plt.ylabel('Margin of safety')
    if mode == 'stringer':
        plt.figure()
        plt.suptitle('Margin of safety for the stringers with regards to compression', y=0.99)

        plt.subplot(311)
        plt.title('Buckling margin of safety', y=1)
        plt.plot(y_lst, margin_stringer_crit)
        plt.xlabel("Spanwise location on the wing (m)")
        plt.ylabel('Margin of safety')
        plt.subplots_adjust(top=0.95, bottom=0.05)

        plt.subplot(312)
        plt.title('Strength margin of safety', y=1)
        plt.plot(y_lst, margin_stringer_strength)
        plt.xlabel("Spanwise location on the wing (m)")
        plt.ylabel('Margin of safety')

        plt.subplot(313)
        plt.title('Combined margin of safety', y=1)
        plt.plot(y_lst, margin_stringer)
        plt.xlabel("Spanwise location on the wing (m)")
        plt.ylabel('Margin of safety')
    

    elif mode == 'tension':
        plt.figure()
        plt.suptitle('Tensional strength of the wingbox')


        plt.subplot(211)
        plt.title("Tensional stress")
        plt.plot(y_lst, tension_stress, label='Applied stress')
        plt.plot([y_lst[0], y_lst[-1]], [strength, strength], 'r', label='Ultimate strength')
        plt.xlabel("Spanwise location on the wing (m)")
        plt.ylabel("Tensional stress (Pa)")
        plt.legend(loc='bottom left')

        plt.subplot(212)
        plt.title("Margin of safety")
        plt.plot(y_lst, margin_stringer_strength)
        plt.xlabel('Spanwise location on the wing (m)')
        plt.ylabel('Margin of safety')
        
    elif mode == 'crack':
        plt.figure()
        plt.suptitle('Crack propagation loads on the wingbox')


        plt.subplot(211)
        plt.title("Maximum stress due to limiting cracks")
        plt.plot(y_lst, stress_crack, label='Applied stress')
        plt.plot([y_lst[0], y_lst[-1]], [crack_strength, crack_strength], 'r', label='Allowed stress')
        plt.xlabel("Spanwise location on the wing (m)")
        plt.ylabel("Stress (Pa)")
        plt.legend(loc='bottom left')

        plt.subplot(212)
        plt.title("Margin of safety")
        plt.plot(y_lst, margin_crack)
        plt.xlabel('Spanwise location on the wing (m)')
        plt.ylabel('Margin of safety')
    
    plt.show()
    return

plot(mode='stringer')