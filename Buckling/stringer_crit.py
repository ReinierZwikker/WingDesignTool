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

I = 0.00000158483 #Moment of inertia per stringer. This still needs to be determined.
E = database_connector.load_wingbox_value("youngs_modulus_pa")
K = 4 #May vary per section in the wingbox. Needs to be determined manually per section.


def crit_stress_stringer(y): #L is the wingbox section length, thus rib spacing. 
    if y <= 10:
        L = 2.5
    if 10 < y <= 20:
        L = 5
    if y > 20:
        L = 6.8
    sigma = (K * (pi ** 2) * E * I) / (L**2)
    return sigma