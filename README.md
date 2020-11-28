# WingDesignTool
Group B05


## How to use the database

Add this at the top of your file:

```python
try:
    import <Modules that dont work here>
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    import <Modules that dont work here>
```

```python
database_connector = DatabaseConnector()
```

When you want to load a value, use:

```python
variable = database_connector.load_value("value_name")
```
  or
```python
variable = database_connector.load_wingbox_value("value_name")
```

Value names should always be lowercase/snakecase. No spaces are allowed in the name.

When you want to save a value, use:

```python
database_connector.save_value("value_name", value)
```
  or
```python
variable = database_connector.save_wingbox_value("value_name")
```
Again only lowercase and underscores!

When you are done with the database, you need to commit the changes to the file!

```python
database_connector.commit_to_database()
```
