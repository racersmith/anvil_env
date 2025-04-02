from anvil.tables import app_tables
import anvil.secrets

from typing import Set, Any


class EnvDB:
    def __init__(self, env_table_name: str):
        self.name = env_table_name
        self.required_columns = {"key", "value"}

        # Lazy load information on request to allow more flexibility in uplink
        self._is_ready = None
        self._table = None
        self._environments = None
        self._environments_enabled = None

    @property
    def is_ready(self) -> bool:
        """Check that the table is setup and ready for use"""
        if self._is_ready is None:
            self._is_ready = self._table_created() and not self._missing_table_columns()
        return self._is_ready

    def _table_created(self) -> bool:
        """Check if the table has been created"""
        return self.name in app_tables

    def _available_columns(self) -> Set[str]:
        if self.table:
            return {col["name"] for col in self.table.list_columns()}
        else:
            return set()
    
    def _missing_table_columns(self) -> Set[str]:
        """Check for missing columns in table"""
        return self.required_columns - self._available_columns()

    @property
    def environments(self) -> Set[str]:
        """ Extra bool columns are assumed to be environments """
        if self._environments is None:
            if self.table:
                environments = set()
                for column in self.table.list_columns():
                    if column['name'] not in self.required_columns and column['type'] == 'bool':
                        environments.add(column['name'])
                self._environments = environments
        return self._environments

    @property
    def environments_enabled(self) -> bool:
        return bool(self.environments)

    @property
    def table(self):
        """get the environment variable app table"""
        if self._table is None:
            if self._table_created():
                self._table = app_tables[self.name]
        return self._table

    def __str__(self) -> str:
        info = f"ENV Table Status: {'Ready' if self.is_ready else 'Requires setup'}\n"
        if self._table_created():
            info += f"\t'{self.name}' table created\n"
        else:
            info += f"\t'{self.name}' table needs to be created\n"

        missing_columns = self._missing_table_columns()
        if missing_columns:
            info += f"\t'{self.name}' missing columns: {', '.join(missing_columns)}"
        else:
            info += f"\t{', '.join(self.required_columns)} columns found"
        return info

    def __repr__(self) -> str:
        return self.__str__()


class _NotSet:
    """ Create a generic object for values that have not been defined yet """
    def __str__(self):
        return 'NotSet'

    def __repr__(self):
        return 'NotSet'
        
NotSet = _NotSet()


class Secret(dict):
    """ We are inheriting from dict so we can use it's serialization in the env table. """
    SIGNATURE = '🔒'
    
    def __init__(self, secret_name: str):
        """ Create a pointer to a value in the Secrets store.

        This provides us with a easy way to add and retrieve secrets from the env table.
        Secrets will be stored in the env table in the form:
            {"🔒": "secret_name"}

        This gives a simple way to add them directly in the table ui with minimal effort.

        Args:
            secret_name: The name of the secret in App Secrets
        """
        self.secret_name = secret_name

        # Package the secret pointer into the super dict.
        super().__setitem__(self.SIGNATURE, secret_name)
        

    def _get_secret(self) -> str:
        return anvil.secrets.get_secret(self.secret_name)

    def __str__(self):
        return f"{self.SIGNATURE}{self.secret_name}"
    
    @classmethod
    def _is_secret(cls, variable: Any):
        """ Check if the variable matches the Secret signature """
        return isinstance(variable, dict) and variable.get(cls.SIGNATURE, False)

    @classmethod
    def _load(cls, variable: dict):
        """ Load the secret """
        return cls(secret_name=variable[cls.SIGNATURE])
        

class Variable:
    def __init__(self, name: str, default: Any):
        self.name = name
        self.default = default
        self._value = NotSet
        self.in_use = False

    @property
    def value(self) -> Any:
        if self._value == NotSet:
            return self.default
        elif isinstance(self._value, Secret):
            # Only fetch the secret on demand
            return self._value._get_secret()
        else:
            return self._value

    @value.setter
    def value(self, value: Any):
        if value == NotSet: 
            raise ValueError("'NotSet' is reservered.")
            
        self.in_use = True
        if Secret._is_secret(value):
            # Load the value in as a Secret
            self._value = Secret._load(value)
        else:
            self._value = value

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __str__(self):
        return str(self.name)

    @property
    def details(self):
        """ Display details about the registered variables """
        return f"{self.name}={self._value}, default={self.default}, in_use={self.in_use}"



class Variables:
    def __init__(self):
        self._all = dict()

    def __str__(self):
        in_use = "\n\t\t".join([str(variable) for variable in self.in_use]) or "No variables in use."
        available = "\n\t\t".join([str(variable) for variable in self.available]) or "No variables available."
        return f"Environment Variables\n\tin_use:\n\t\t{in_use}\n\tavailable:\n\t\t{available}"

    @property
    def detailed(self):
        in_use = "\n\t".join([variable.details for variable in self.in_use]) or "No variables in use."
        available = "\n\t".join([variable.details for variable in self.available]) or "No variables available."
        print(f"Environment Variables\nin_use:\n\t{in_use}\navailable:\n\t{available}")
    
    def __repr__(self):
        return self.__str__()

    def _register(self, variable: Variable):
        """Add variable as currently in use from db"""
        self._all[variable.name] = variable
    
    @property
    def all(self):
        """Get a set of all registered variable names"""
        return set(self._all.values())

    @property
    def in_use(self):
        """Get a set of variable names that are being set from the env table"""
        return set(filter(lambda var: var.in_use, self.all))

    @property
    def available(self):
        """Get a set of varible names that are utilizing their default value
        and not present in the env table.
        """
        return set(filter(lambda var: not var.in_use, self.all))
