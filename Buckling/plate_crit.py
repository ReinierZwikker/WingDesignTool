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
kc = 0 #Might vay per section. Kc needs to be determined manually per section
t = database_connector.load_wingbox_value("plate_thickness")


def plate_crit_force(b): # b is the stringer spacing
    Fcr = (((pi**2)*kc*E) / (12*(1-(pois**2)))) * ((t/b)**2)
    return Fcr


def plate_crit_stress(b): # b is the stringer spacing
    sigma = plate_crit_force(b) / (t*b)
    return sigma