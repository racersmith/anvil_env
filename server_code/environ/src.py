from anvil import tables
from anvil.tables import Row, Table
from anvil import app

from anvil import _AppInfo

from . import models

from typing import Any, Set, Iterable
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


def _normalize_environment_request(environments: dict | Iterable | str | None, availble_envrionments: Set) -> dict:
    """ Normalize the environment search request
    This normalizes the request form and verifies the environments
    
    Only True environments are returned in the results except for the special None case,
    which populates all available_environments with None.
    
    Examples:
        available_environments = {'A', 'B', 'C'}
        
        environments = {'A': True, 'B': False, 'C': None}
        environments = ['A']
        environments = 'A'
        >> {'A': True}

        envrionments = 'A', 'B'
        >> {'A': True, 'B': True}

        environments = None
        >> {'A': None, 'B': None, 'C': None}
    """
    
    if isinstance(environments, dict):
        request = dict()
        for env, value in environments.items():
            if value not in {True, False, None}:
                raise TypeError(f"environments dict must include only bool values or None. recieved: {value}")

            if env not in availble_envrionments:
                raise LookupError(f"{env} not found in list of available environments.")

            # Strip out only the True values and discard all None/False
            if value:
                request[env] = value
        return request

    # Single environment given as string
    if isinstance(environments, str):
        if environments not in availble_envrionments:
                raise LookupError(f"{environments} not found in list of available environments.")
        return {environments: True}

    # Default lookup case
    if environments is None:
        return {env: None for env in availble_envrionments}

    # Iterable case
    try:
        request = dict()
        for env in environments:
            if env not in availble_envrionments:
                raise LookupError(f"{env} not found in list of available environments.")
            request[env] = True
        return request
    except TypeError as e:
        raise TypeError(f"Expected a dict, iterable, str or None. recieved: {environments}") from e
        

def set(
    name: str, value: Any, environments: dict | Iterable | None = None, info: str | None = None
) -> None:
    """Set an environment variable
    Args:
        name: name of the variable to set
        value: value for the variable, can be any standard python object
        environments: provide a dict with the enabled environments for this variable, a list of active envrionments or None for a default var.
        info: human-readable information about the environment varaible
    """

    if environments and not DB.environments_enabled:
        raise NotImplementedError(
            f"Environments have not been enabled in the '{DB.name}' table.  Add bool columns for each environment ie. 'Published', 'Debug'"
        )

    if DB.is_ready:
        search = {"key": name}
        
        env_request = _normalize_environment_request(environments, DB.environments)
        search.update(**env_request)

        # find or create the row
        row = DB.table.get(**search) or DB.table.add_row(**search)

        # Add the variable information
        update = {"value": value, "info": info}
        row.update({k: v for k, v in update.items() if k in row.keys()})
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
    if db.environments_enabled and environment is not None:
        environment = resolve_environment(environment.name, db.environments)
        env_request = _normalize_environment_request(environment, db.environments)
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
        env_request = _normalize_environment_request(None, db.environments)
        search.update(env_request)
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
