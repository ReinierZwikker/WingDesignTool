### ------ Workpackage 4.1: Inertial loading calculations ------ ###
import scipy
from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()

# Import basic geometry
b = database_connector.load_value("wing_span")
d_fus = database_connector.load_value("df,outer")
r_fus = d_fus / 2

# Import lift distribution function
from filename import liftfunctionname as L

# Import weight and location of the engine
W_eng = database_connector.load_value("engine_weight")
y_eng = database_connector.load_value("engine_spanwise_location")

# Calculate/Import the weight of the wing (use fraction from class II)
W_wing = database_connector.load_value("wing_weight")

# Calculate final lift distribution
L_final = L - W_wing

# Calculate the moment function from the tip to the engine (excluding engine)
# Moment @ tip equals zero

M1 = scipy.integrate.quad(L_final, y_eng, b / 2)

# Calculate the moment function from the engine (including) to the fuselage
# Moment @ engine equals the max moment minus the weight of the engine

M2 = scipy.integrate.quad(L_final, r_fus, y_eng)
