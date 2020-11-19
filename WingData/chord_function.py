try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()

chord_r = database_connector.load_value("root_chord")
taper = database_connector.load_value("taper_ratio")
half_span = database_connector.load_value("wing_span") / 2

#Determines the chord length at every y position along the span
def chord_function(y):
    return chord_r - chord_r*(1-taper)*(y/half_span)