from anvil.tables import app_tables

def set(variable: str, value, info: str | None = None):
    # Set an environment variable
    return (
        app_tables.env.get(key=variable)
        or app_tables.env.add_row(key=variable, value=value, info=info)
    )

def get(variable: str, default=LookupError):
    """ Get an environment variable """
    row = app_tables.get(key=variable)
    if row is None:
        if default is LookupError:
            raise LookupError(f"'{variable}' not found")
        else:
            return default
    return row['value']


        
