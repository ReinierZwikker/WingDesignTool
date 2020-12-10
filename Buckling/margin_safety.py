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
    from Buckling.stringer_applied import string_stress_normal
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


margin_stringer_crit = []
margin_stringer_strength = []
margin_stringer = []
for y in y_lst:
    margin_stringer_crit.append(margin_safety_crit(string_stress_normal(y), crit_stress_stringer(y)))
    margin_stringer_strength.append(margin_safety_strength(string_stress_normal(y)))
    margin_stringer.append(min(margin_stringer_crit[-1], margin_stringer_strength[-1]))
    #add the same for plate and spars


plt.plot(y_lst, margin_stringer_crit)
plt.plot(y_lst, margin_stringer_strength)
plt.plot(y_lst, margin_stringer)
