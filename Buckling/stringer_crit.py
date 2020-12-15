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
    if y <= 4:
        L = 4
    if 4 < y <= 8:
        L = 4
    if 8 < y <= 12:
        L = 4
    if 12 < y <= 16:
        L = 4
    if 16 < y <= 20:
        L = 4
    if 20 < y <= 24:
        L = 4
    if 24 < y <= 27:
        L = 2.8
    sigma = (K * (pi ** 2) * E * I) / (L**2)
    return sigma