from anvil.tables import app_tables


class EnvDB:
    def __init__(self, env_table_name: str):
        self.name = env_table_name
        self.required_columns = {"key", "value", "info"}
        self.is_ready = self._is_ready()
        self.table = self._get_table()
    
    def _is_ready(self):
        """Check that the table is setup and ready for use"""
        return self._table_created() and not self._missing_table_columns()

    def _table_created(self) -> bool:
        """Check if the table has been created"""
        return self.name in app_tables

    def _missing_table_columns(self) -> set:
        """Check for missing columns in table"""
        table_cols = set()
        table = self._get_table()
        if table:
            table_cols = {col["name"] for col in table.list_columns()}
        return self.required_columns - table_cols

    def _get_table(self):
        """get the environment variable app table"""
        if self._table_created():
            return app_tables[self.name]
        else:
            return None

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
    def __str__(self):
        return 'NotSet'

    def __repr__(self):
        return 'NotSet'
        
NotSet = _NotSet()


class Variable:
    def __init__(self, name: str, default):
        self.name = name
        self.default = default
        self._value = NotSet
        self.in_use = False

    @property
    def value(self):
        if self._value == NotSet:
            return self.default
        else:
            return self._value

    @value.setter
    def value(self, value):
        assert value != NotSet, "'NotSet' is reservered."
        self.in_use = True
        self._value = value

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __str__(self):
        return str(self.name)

    @property
    def details(self):
        return f"{self.name}={self.value}, default={self.default}, in_use={self.in_use}"



class Variables:
    def __init__(self):
        self._all = set()
        self._in_use = set()
        self._available = set()

    def __str__(self):
        in_use = "\n\t".join([str(variable) for variable in self.in_use]) or "No variables in use."
        available = "\n\t".join([str(variable) for variable in self.available]) or "No variables available."
        return f"Environment Variables\nin_use:\n\t{in_use}\navailable:\n\t{available}"

    @property
    def detailed(self):
        in_use = "\n\t".join([variable.details for variable in self.in_use]) or "No variables in use."
        available = "\n\t".join([variable.details for variable in self.available]) or "No variables available."
        print(f"Environment Variables\nin_use:\n\t{in_use}\navailable:\n\t{available}")
    
    def __repr__(self):
        return self.__str__()

    def _register(self, variable: Variable):
        """Add variable as currently in use from db"""
        self._all.add(variable)
        if variable.in_use:
            self._in_use.add(variable)
        else:
            self._available.add(variable)
    
    @property
    def all(self):
        """Get a set of all registered variable names"""
        return self._all

    @property
    def in_use(self):
        """Get a set of variable names that are being set from the env table"""
        return self._in_use

    @property
    def available(self):
        """Get a set of varible names that are utilizing their default value
        and not present in the env table.
        """
        return self._available
