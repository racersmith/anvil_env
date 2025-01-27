from anvil.tables import app_tables
from anvil import tables


def _env_ready():
    """Check if the env table has been setup and is ready for use"""
    if 'env' not in app_tables:
        print("'env' table not created")
        return False

    cols = {col['name'] for col in app_tables.env.list_columns()}
    if {'key', 'value', 'info'} != cols:
        print("'env' table columns not matching")
        return False

    return True


class _STATUS:
    def __init__(self):
        self._in_use = set()
        self._available = set()
        self._status = _env_ready()

    def __str__(self):
        in_use = "\n\t".join(self.in_use)
        available = "\n\t".join(self.available)
        return f"in_use:\n\t{in_use}\navailable\n\t{available}"
    
    @property
    def all(self):
        return self.in_use | self.available

    @property
    def in_use(self):
        return self._in_use

    def _register_in_use(self, variable: str):
        """Add variable as currently in use from db"""
        self._in_use.add(variable)

    @property
    def available(self):
        return self._available

    def _register_available(self, variable: str):
        """Add variable is availble to override in db"""
        self._available.add(variable)


REGISTERED = _RegisteredVariables()



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
        REGISTERED._register_in_use(variable)
    else:
        raise tables.TableError("'env' tabl enot set up.")


def get(variable: str, default=LookupError):
    """Get an environment variable"""
    if _is_ready:
        row = app_tables.env.get(key=variable)
        if row:
            REGISTERED._register_in_use(variable)
            return row["value"]
    else:
        print(f"'env' not setup, returning default value for: {variable}")

    REGISTERED._register_available(variable)
    if default is LookupError:
        raise LookupError(f"environment variable: '{variable}' not found")
    else:
        return default
        