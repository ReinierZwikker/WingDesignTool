import matplotlib.pyplot as plt

try:
    import Importer.xflr5 as aerodynamic_data
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    import Importer.xflr5 as aerodynamic_data
    from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()

# Import basic geometry
wing_span = database_connector.load_value("wing_span")
Outer_diameter = database_connector.load_value("df,outer")
radius_fuselage = Outer_diameter / 2
surface_area = database_connector.load_value("surface_area")
# Import weight and location of the engine
weight_engine = database_connector.load_value("engine_weight")
spanwise_location_engine = database_connector.load_value("engine_spanwise_location")
# Import the weight of the wing and fuel (Class II)
weight_wing = database_connector.load_value("wing_weight")
weight_fuel = database_connector.load_value("fuel_max")

def lift_distribution(y, density, velocity):
    return aerodynamic_data.lift_coef_function_10(y) * 0.5 * density * (velocity ** 2) * surface_area

density_FBD = 1.225
velocity_FBD = database_connector.load_value("cruise_speed")
length_steps = 0.5
i = radius_fuselage

lift_force_list = []
wing_weight_list =[]
engine_weight_list = []
y_location_list =[]
wing_list = []

while i <= wing_span/2:

    lift_force = lift_distribution(i,density_FBD,velocity_FBD)
    lift_force_list.append(lift_force)
    wing_weight_list.append(-weight_wing)
    wing_list.append(0)

    if i == spanwise_location_engine:
        engine_weight_list.append(-weight_engine)
    else:
        engine_weight_list.append(0.0)

    y_location_list.append(i)
    i += length_steps

plt.stem(y_location_list,lift_force_list,use_line_collection=True)
plt.stem(y_location_list,wing_weight_list,use_line_collection=True)
plt.plot(spanwise_location_engine, weight_engine, 'r')
plt.plot(y_location_list,wing_list,'black')
plt.xlabel("y-location [m]")
plt.ylabel("Force [N]")
plt.show()