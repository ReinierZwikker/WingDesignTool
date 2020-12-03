try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector


# impoerting form wingbox database
t_spar = DatabaseConnector.load_wingbox_value("spar_thickness")

