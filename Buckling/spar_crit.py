from math import *

try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()

pois = database_connector.load_wingbox_value("poisson_ratio")
E = database_connector.load_wingbox_value("youngs_modulus_pa")
ks = 0 #Might vay per section. Ks need to be determined manually per section
t = database_connector.load_wingbox_value("spar_thickness")


def spar_crit_stress(b): #b is the height of the spar
    stress = (((pi**2)*ks*E) / (12*(1-(pois**2)))) * ((t/b)**2)
    return stress 