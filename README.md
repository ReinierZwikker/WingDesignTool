# WingDesignTool
Group B05


## How to use the database

Add this at the top of your file:

`from Database.database_functions import DatabaseConnector`

`database_connector = DatabaseConnector()`

When you want to load a value, use:

`variable = database_connector.load_value("value_name")`
  or
`variable = database_connector.load_wingbox_value("value_name")`

Value names should always be lowercase/snakecase. No spaces are allowed in the name.

When you want to save a value, use:

`database_connector.save_value("value_name", value)`

Again only lowercase and underscores!

When you are done with the database, you need to commit the changes to the file!

`database_connector.commit_to_database()` 
