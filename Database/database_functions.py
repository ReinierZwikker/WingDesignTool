import json
import os
import inspect


class DatabaseConnector:

    def __init__(self):
        self.__database_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        self.__database_file = self.__database_folder + '/database.json'
        self.__wingbox_file = self.__database_folder + '/wingbox.json'
        with open(self.__database_file) as database:
            self.__database_dict = json.load(database)
        with open(self.__wingbox_file) as wingbox:
            self.__wingbox_dict = json.load(wingbox)
        with open(self.__database_file + str(1), "w") as databackup:
            json.dump(self.__database_dict, databackup)

    def reload_database(self):
        self.__init__()

    def load_value(self, name):
        try:
            return self.__database_dict[name.lower().replace(" ", "_")]
        except KeyError:
            print("This value does not exist!")
            return None

    def load_wingbox_value(self, name):
        try:
            return self.__wingbox_dict[name.lower().replace(" ", "_")]
        except KeyError:
            print("This value does not exist!")
            return None

    def save_value(self, name, value):
        self.__database_dict[name] = value

    def commit_to_database(self):
        with open(self.__database_file + str(2), "w") as databackup:
            json.dump(self.__database_dict, databackup)
        with open(self.__database_file, "w") as database:
            json.dump(self.__database_dict, database, indent=4)

    def preview_database(self):
        for element in self.__database_dict:
            print(f"{element}: {self.__database_dict[element]}")

    def cleanup_database(self):
        if input("Are you sure you want to clean up the database? (Y/n)") == "Y":
            for element in self.__database_dict:
                self.__database_dict[element.lower()] = self.__database_dict.pop(element)
            self.commit_to_database()
            print("Database cleaned up!")

