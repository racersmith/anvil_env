from anvil import tables

from . import models

# you can change the name of your table here.
DB = models.EnvDB(env_table_name='env')

# track the usage of environment variables
VARIABLES = models.Variables()


def set(variable: str, value, info: str | None = None) -> None:
    """Set an environment variable
    Args:
        variable: name of the variable to set
        value: value for the variable, can be any standard python object
        info: human readable information about the environment varaible
    """    
    if DB.is_ready:
        row = (
            DB.table.get(key=variable)
            or DB.table.add_row(key=variable)
        )
        
        row['value'] = value
        row['info'] = info
        VARIABLES._register_in_use(variable)
    else:
        raise tables.TableError("'env' tabl enot set up.")


def get(variable: str, default=LookupError):
    """Get an environment variable"""
    if DB.is_ready:
        row = DB.table.get(key=variable)
        if row:
            VARIABLES._register_in_use(variable)
            return row["value"]
    else:
        print(f"'env' not setup, returning default value for: {variable}")

    VARIABLES._register_available(variable)
    if default is LookupError:
        raise LookupError(f"environment variable: '{variable}' not found")
    else:
        return default
        