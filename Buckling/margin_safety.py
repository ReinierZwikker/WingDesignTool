try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()

strength = database_connector.load_wingbox_value("ultimate_strength")


def margin_safety_crit(applied, crit):
    factor = crit/applied
    return factor

def margin_safety_strength(applied):
    factor = strength/applied
    return factor