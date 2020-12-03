


try:
    from Database.database_functions import DatabaseConnector
    from Twist.twist_calc import dtheta_multi, lift_distribution, drag_distribution
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector
    from Twist.twist_calc import dtheta_multi, lift_distribution, drag_distribution


database_connector = DatabaseConnector()


# importing form wing-box database
t_spar = database_connector.load_wingbox_value("spar_thickness")


# def shear_lift




