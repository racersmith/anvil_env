from anvil import tables
from anvil.tables import Row, Table
from anvil import app

from anvil import _AppInfo

from . import models

from typing import Any, Set
import logging

logger = logging.getLogger(__name__)

# you can change the name of your table here.
DB = models.EnvDB(env_table_name="env")

# track the usage of environment variables
VARIABLES = models.Variables()

# Check if we are in the published or development mode
ENVIRONMENT = app.environment


def info():
    """Display info about ENV"""
    s = ["ENV"]
    s.append(f"Environment: {ENVIRONMENT.name}")
    s.append(f"App branch: {app.branch}")
    s.append(f"Table name: {DB.name}")
    s.append(f"Table ready: {DB.is_ready}")
    if not DB.is_ready:
        s.append(f"  Table '{DB.name}' created: {DB._table_created()}")
        s.append(f"  Missing columns: {DB._missing_table_columns()}")
    s.append(f"\n{VARIABLES}")
    print("\n".join(s))


def resolve_environment(
    current_environment: str, available_environments: Set[str]
) -> str:
    """Find which of the available table environments best match the given environment"""
    if current_environment in available_environments:
        # Check for the direct match of environment name
        return current_environment
    else:
        # Check for a generic environment ie 'Debug for abc@example.com' -> 'Debug'
        matching = list(
            filter(
                lambda env: current_environment.startswith(env), available_environments
            )
        )
        if len(matching) == 1:
            return matching[0]
        # elif len(matching) == 0:
        #     raise LookupError(f"Not able to resolve the environment: '{current_environment}' to any of {available_environments}")
        elif len(matching) > 1:
            raise LookupError(
                f"Environment: '{current_environment}' matches more than one environment: {matching}"
            )
    return None


def set(
    name: str, value: Any, environments: dict | None = None, info: str | None = None
) -> None:
    """Set an environment variable
    Args:
        name: name of the variable to set
        value: value for the variable, can be any standard python object
        info: human readable information about the environment varaible
        environments: provide a dict with the enabled environments for this variable or None to enable for all.
    """

    if environments and not DB.environments_enabled:
        raise NotImplementedError(
            f"Environments have not been enabled in the '{DB.name}' table.  Add bool columns for each environment ie. 'Published', 'Debug'"
        )

    if DB.is_ready:
        search = {"key": name}
        if environments:
            search.update(**environments)
        elif DB.environments_enabled and environments is None:
            # Create the default variable with all environments set to None
            search.update(DB._get_default_env())

        # find or create the row
        row = DB.table.get(**search) or DB.table.add_row(**search)

        # Add the variable information
        row.update({"value": value, "info": info})
    else:
        raise tables.TableError(f"'{DB.name}' table not set up.")


def _try_lookup(search: dict, table: Table) -> Row | None:
    """Serach for a row and give feedback on multiple matches"""
    try:
        row = table.get(**search)
    except tables.TableError as e:
        if e.message == "More than one row matched this query":
            raise tables.TableError(
                f"Do you have two entries for '{search}', ensure there are no overlapping environments for the variable."
            ) from e
        else:
            raise e
    return row


def _get_value(
    variable: models.Variable, db: models.EnvDB, environment: _AppInfo._Environment
) -> models.Variable:
    """Get an environment variable
    Args:
        variable, variable object
        db: EnvDb object
        environment: The environment that the app is running in from anvil.app.environment

    Returns:
        variable object.
    """
    search = {"key": variable.name}
    # search.update(db._get_default_env())
    row = None
    if db.environments_enabled:
        environment = resolve_environment(environment.name, db.environments)
        if environment:
            # Set our search to the current environment
            search[environment] = True
            row = _try_lookup(search, db.table)

    if row is None:
        """ 
        we are here because one of:
            1. environments are not enabled
            2. we were unable to resolve the current environment
            3. there was no entry for the environment specified and we are looking for a default
        These all have the same solution of looking for the row that matches with the default env.
        """
        search.update(db._get_default_env())
        row = _try_lookup(search, db.table)

    if row is not None:
        # Assign the variable value if one was found
        variable.value = row["value"]

    # this return is not strictly necessary since we are updating the variable object.
    return variable


def get(name: str, default=models.NotSet) -> Any:
    """Get an environment variable and register it's use
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
        variable = _get_value(variable, DB, ENVIRONMENT)

    else:
        logger.info(f"'env' not setup, returning default value for: {variable}")

    value = variable.value
    if value == models.NotSet:
        raise LookupError(
            f"env: {variable.name} not found in '{DB.name}' and no default value given."
        )

    VARIABLES._register(variable)
    return value
