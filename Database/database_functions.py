import json


class DatabaseConnector:

    def __init__(self):
        self.database_file = './database.json'
        with open(self.database_file) as database:
            self.database_dict = json.load(database)
        with open(self.database_file + str(1), "w") as databackup:
            json.dump(self.database_dict, databackup)

    def reload_database(self):
        self.__init__()

    def load_value(self, name):
        try:
            return self.database_dict[name.lower().replace(" ", "_")]
        except KeyError:
            print("This value does not exist!")
            return None

    def save_value(self, name, value):
        self.database_dict[name] = value

    def commit_to_database(self):
        with open(self.database_file + str(2), "w") as databackup:
            json.dump(self.database_dict, databackup)
        with open(self.database_file, "w") as database:
            json.dump(self.database_dict, database, indent=4)

    def preview_database(self):
        for element in self.database_dict:
            print(f"{element}: {self.database_dict[element]}")

    def cleanup_database(self):
        if input("Are you sure you want to clean up the database? (Y/n)") == "Y":
            for element in self.database_dict:
                self.database_dict[element.lower()] = self.database_dict.pop(element)


database_connector = DatabaseConnector()
database_connector.cleanup_database()

