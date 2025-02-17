from anvil import tables
from anvil.tables import Row, Table
import anvil.tables.query as q
from anvil import app
from . import models

import logging
logger = logging.getLogger(__name__)

# you can change the name of your table here.
DB = models.EnvDB(env_table_name='env')

# track the usage of environment variables
VARIABLES = models.Variables()

# Check if we are in the published or development mode
DEVELOPMENT_MODE = 'debug' in app.environment.tags


def set(variable: str, value, info: str | None = None, development: bool=False) -> None:
    """Set an environment variable
    Args:
        variable: name of the variable to set
        value: value for the variable, can be any standard python object
        info: human readable information about the environment varaible
        development: Value is used for development environments only
    """    
    if DB.is_ready:
        row = (
            DB.table.get(key=variable)
            or DB.table.add_row(key=variable)
        )
        
        row['value'] = value
        row['info'] = info
        row['development'] = development
        VARIABLES._register_in_use(variable)
    else:
        raise tables.TableError("'env' table not set up.")


def _get_production_row(name: str, table: Table) -> Row | None:
    """ Get any the key row that is not flagged as development only. """
    try:
        row = table.get(key=name, development=q.any_of(False, None))
    except tables.TableError as e:
        if e.message == 'More than one row matched this query':
            raise tables.TableError(f"Do you have two entries for '{name}' with development=None and development=False?") from e
        else:
            raise e
    return row


def _get_development_row(name: str, table: Table) -> Row | None:
    """ Get the development only row if available or the production row """
    return table.get(key=name, development=True) or _get_production_row(name, table)
    

def _get_value(variable: models.Variable, db: models.EnvDB, development_mode: bool) -> models.Variable:
    """Get an environment variable
    Args:
        variable, variable object
        db: EnvDb object
        development_mode: is this a development environment?  Prod = False, debug = True

    Returns:
        variable object.
    """

    if development_mode:
        # Get the development version if available and fall back to prod variables
        row = _get_development_row(variable.name, db.table)
    else:
        # Only allow the retrieval of production variables
        row = _get_production_row(variable.name, db.table)
        
    if row is not None:
        # Assign the variable value if one was found
        variable.value = row['value']

    # this return is not strictly necessary since we are updating the variable object.
    return variable
    


def get(name: str, default=models.NotSet):
    """Get an environment variable
    Args:
        name, name of variable
        default, value to return if the varible is not available

    Returns:
        the object from the env table or the default value if set.

    Raises:
        rasies a LookupError if the varible is not available in the env table and no
        default value is given.
    """
    variable = models.Variable(name, default)
    if DB.is_ready:
        variable = _get_value(variable, DB, DEVELOPMENT_MODE)
        
    else:
        logger.info(f"'env' not setup, returning default value for: {variable}")

    value = variable.value
    if value == models.NotSet:
        raise LookupError(f"env: {variable.name} not found in '{DB.name}' and no defualt value given.")

    VARIABLES._register(variable)
    return value
        