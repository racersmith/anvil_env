from anvil.tables import app_tables
import anvil.server


class EnvDB:
    def __init__(self, env_table_name: str):
        self.name = env_table_name
        self.required_columns = {"key", "value", "info"}
        self.is_ready = self._is_ready()
        self.table = self._get_table()

    def _get_table(self):
        """get the environment variable app table"""
        if self._table_created:
            return app_tables[self.name]
        else:
            return None

    def _is_ready(self):
        """Check that the table is setup and ready for use"""
        return self._table_created() and not self._missing_table_columns()

    def _table_created(self) -> bool:
        return self.name in app_tables

    def _missing_table_columns(self) -> set:
        table_cols = set()
        if table:=self._get_table():
            table_cols = {col["name"] for col in table.list_columns()}
        return self.required_columns - table_cols

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


class Variables:
    def __init__(self):
        self._in_use = set()
        self._available = set()

    def __str__(self):
        in_use = "\n\t".join(self.in_use) or "No variables in use."
        available = "\n\t".join(self.available) or "No variables available."
        return f"Environment Variables\nin_use:\n\t{in_use}\navailable:\n\t{available}"

    def __repr__(self):
        return self.__str__()
    
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
