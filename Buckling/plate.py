from math import *

try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()

pois = 
E = database_connector.load_wingbox_value("stringer_modulus")
k = 0 #Dont know yet
def plate_crit_force():
    Fcr = ((pi**2)*k*E) / (12*(1-))