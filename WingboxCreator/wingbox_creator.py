import json
try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()

wingbox_file = '../Database/wingbox.json'

halfspan = database_connector.load_value("wing_span")/2
quarter_chord_sweep = database_connector.load_value("quarter_chord_sweep")
dihedral_angle = database_connector.load_value("dihedral_angle")


wingbox_definition = {'length': halfspan,
                      'height': 0.2,
                      'width':  23,
                      'quarter_chord_sweep': quarter_chord_sweep,
                      'dihedral_angle': dihedral_angle,
                      'stringers_top': [0.1, 0.2, 0.5, 0.7, 0.9],     # Stringer location from LE to TE as fraction of wingbox width
                      'stringers_bottom': [0.1, 0.2, 0.5, 0.7, 0.9],  # Stringer location from LE to TE as fraction of wingbox width
                      'stringers_leading': [0.2, 0.5, 0.7],           # Stringer location from bottom to top as fraction of wingbox height
                      'stringers_trailing': [0.2, 0.5, 0.7],          # Stringer location from bottom to top as fraction of wingbox height
                      'ribs': [0.1, 0.2, 0.5, 0.7, 0.9],              # Rib location from root to tip as fraction of wingbox length
                      'stiffeners': [0.1, 0.2, 0.3, 0.5, 0.6, 0.7, 0.9],        # Stiffener location from root to tip as fraction of wingbox length
                      'sheet_thickness': 0.1,
                      'stringer_thickness': 0.1,
                      'rib_thickness': 0.1,
                      'stiffener_thickness': 0.1
                      }


with open(wingbox_file, "w") as wingbox_database:
    json.dump(wingbox_definition, wingbox_database, indent=4)
