from math import *

try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()

I = 0 # Moment of inertia per stringer
E = database_connector.load_wingbox_value("stringer_modulus")
K = 4 #May vary per section in the wingbox


def crit_stress_stringer(L): #L is the wingbox section length, thus rib spacing
    sigma = (K * (pi ** 2) * E * I) / (L**2)
    return sigma