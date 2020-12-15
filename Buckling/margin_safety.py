import pickle
import matplotlib.pyplot as plt

try:
    from Database.database_functions import DatabaseConnector
    from Buckling.stringer_applied import string_stress_normal
    from Buckling.stringer_crit import crit_stress_stringer
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    from Buckling.stringer_applied import string_stress_normal, string_stress_tension
    from Buckling.stringer_crit import crit_stress_stringer

database_connector = DatabaseConnector()

try:
    with open("../InertialLoadingCalculator/data.pickle", 'rb') as file:
        data = pickle.load(file)
except FileNotFoundError:
    with open("./data.pickle", 'rb') as file:
        data = pickle.load(file)

y_lst = data[0]
strength = database_connector.load_wingbox_value("ultimate_strength")


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
    for y in y_lst:
        if mode == 'compression':
            margin_stringer_crit.append(margin_safety_crit(string_stress_normal(y), crit_stress_stringer(y)))
            margin_stringer_strength.append(margin_safety_strength(string_stress_normal(y)))
            margin_stringer.append(min(margin_stringer_crit[-1], margin_stringer_strength[-1]))
        
            #add the same for plate and spars
        if mode == 'tension':
            margin_stringer_strength.append(margin_safety_strength(string_stress_tension(y)))

            #add the same for plate and spars
            
    if mode == 'compression':
        plt.figure()
        plt.suptitle('Compressive margin of safety per component')

        plt.subplot(131)
        plt.title('Buckling stringer')
        plt.plot(y_lst, margin_stringer_crit)

        plt.subplot(132)
        plt.title('Strength stringer')
        plt.plot(y_lst, margin_stringer_strength)

        plt.subplot(133)
        plt.title('Combined stringer')
        plt.plot(y_lst, margin_stringer)
    
        #add the same for plate and spars

    elif mode == 'tension':
        plt.figure()
        plt.suptitle('Tensional margin of safety per component')

        plt.subplot(311)
        plt.title("Stringer")
        plt.plot(y_lst, margin_stringer_strength)

        #add the same for plate and spars
    
    plt.show()
    return

plot(mode='compression')