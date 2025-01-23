from anvil.tables import app_tables
from anvil import tables


# @tables.in_transaction
def set(variable: str, value, info: str | None = None) -> None:
    # Set an environment variable
    row = (
        app_tables.env.get(key=variable)
        or app_tables.env.add_row(key=variable)
    )
    
    row['value'] = value
    row['info'] = info


# @tables.in_transaction
def get(variable: str, default=LookupError):
    """Get an environment variable"""
    row = app_tables.env.get(key=variable)
    if row is None:
        if default is LookupError:
            raise LookupError(f"'{variable}' not found")
        else:
            return default
    return row["value"]
