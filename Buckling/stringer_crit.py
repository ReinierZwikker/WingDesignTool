from math import *
import matplotlib.pyplot as plt
import numpy as np

try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()

I = # Moment of inertia per stringer. This still needs to be determined.
E = database_connector.load_wingbox_value("youngs_modulus_pa")
K = 4 #May vary per section in the wingbox. Needs to be determined manually per section.


def crit_stress_stringer(y): #L is the wingbox section length, thus rib spacing. 
    if y < 4:
        L = ..
    if .. < y < ..:
        L = ..
    if .. < y < ..:
        L = ..
    sigma = (K * (pi ** 2) * E * I) / (L**2)
    return sigma