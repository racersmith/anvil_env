from anvil.tables import app_tables
from anvil import tables


def set(variable: str, value, info: str | None = None) -> None:
    """Set an environment variable
    Args:
        variable: name of the variable to set
        value: value for the variable, can be any standard python object
        info: human readable information about the environment varaible
    """
    row = (
        app_tables.env.get(key=variable)
        or app_tables.env.add_row(key=variable)
    )
    
    row['value'] = value
    row['info'] = info


def get(variable: str, default=LookupError):
    """Get an environment variable"""
    row = app_tables.env.get(key=variable)
    if row is None:
        if default is LookupError:
            raise LookupError(f"environment variable: '{variable}' not found")
        else:
            return default
    return row["value"]
