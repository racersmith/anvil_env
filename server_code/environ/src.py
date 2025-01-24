from anvil.tables import app_tables
from anvil import tables

def _env_ready():
    if 'env' not in app_tables:
        print("'env' table not created")
        return False

    cols = {col['name'] for col in app_tables.env.list_columns()}
    if {'key', 'value', 'info'} != cols:
        print("'env' table columns not matching")
        return False

    return True

_is_ready = _env_ready()

def set(variable: str, value, info: str | None = None) -> None:
    """Set an environment variable
    Args:
        variable: name of the variable to set
        value: value for the variable, can be any standard python object
        info: human readable information about the environment varaible
    """
    if _is_ready:
        row = (
            app_tables.env.get(key=variable)
            or app_tables.env.add_row(key=variable)
        )
        
        row['value'] = value
        row['info'] = info
    else:
        raise tables.TableError("'env' tabl enot set up.")


def get(variable: str, default=LookupError):
    """Get an environment variable"""
    if _is_ready:
        row = app_tables.env.get(key=variable)
        if row:
            return row["value"]
    else:
        print(f"'env' not setup, returning default value for: {variable}")
    
    if default is LookupError:
        raise LookupError(f"environment variable: '{variable}' not found")
    else:
        return default
        
