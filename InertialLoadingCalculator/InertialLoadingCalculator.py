### ------ Workpackage 4.1: Inertial loading calculations ------ ###
import scipy
import numpy as np
from Database.database_functions import DatabaseConnector
database_connector = DatabaseConnector()
import Importer.xflr5

#Import basic geometry
wing_span = database_connector.load_value("wing_span")
Outer_diameter = database_connector.load_value("df,outer")
radius_fuselage = Outer_diameter/2
surface_area = database_connector.load_value("surface_area")

#Define the flight conditions
velocity = 0.0 #m/s
density = 0.0 #kg/m^2

#Import weight and location of the engine
weight_engine = database_connector.load_value("engine_weight")
spanwise_location_engine = database_connector.load_value("engine_spanwise_location")

#Import the weight of the wing and fuel (Class II)
weight_wing = database_connector.load_value("wing_weight")
weight_fuel = database_connector.load_value("fuel_max")



#Define the lift distribution
def lift_distribution(y):
    return xflr5.lift_coef_function_0(y)* 0.5 * density * velocity^2 * surface_area

#Calculate the final force distribution
def final_force_distribution(y):
    #if  spanwise_location_engine < y:
    return lift_distribution(y) - weight_wing - weight_fuel
    #elif y == spanwise_location_engine:
    #    return lift_distribution(y) - weight_wing - weight_fuel - weight_engine

#Integrate to shear function
def shear_force_function(y):
    return 


