try:
    from Database.database_functions import DatabaseConnector
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from Database.database_functions import DatabaseConnector

database_connector = DatabaseConnector()


def get_amount_of_stringers(spanwise_location, top):
    amount_of_stringers = 0
    if top:
        if spanwise_location < database_connector.load_wingbox_value('top_stringer_lim_point_1'):
            amount_of_stringers += database_connector.load_wingbox_value('top_number_of_stringers_1')
        elif spanwise_location < database_connector.load_wingbox_value('top_stringer_lim_point_2'):
            amount_of_stringers += database_connector.load_wingbox_value('top_number_of_stringers_2')
        else:
            amount_of_stringers += database_connector.load_wingbox_value('top_number_of_stringers_3')
    if not top:
        if spanwise_location < database_connector.load_wingbox_value('bottom_stringer_lim_point_1'):
            amount_of_stringers += database_connector.load_wingbox_value('bottom_number_of_stringers_1')
        elif spanwise_location < database_connector.load_wingbox_value('bottom_stringer_lim_point_2'):
            amount_of_stringers += database_connector.load_wingbox_value('bottom_number_of_stringers_2')
        else:
            amount_of_stringers += database_connector.load_wingbox_value('bottom_number_of_stringers_3')
    if spanwise_location < 10:
        amount_of_stringers += 4
    else:
        amount_of_stringers += 2
    return amount_of_stringers
