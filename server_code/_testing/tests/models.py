import anvil.tables

from ...environ import models

class TestEnvDB:
    def test_good_table(self):
        db = models.EnvDB('env')
        assert db.is_ready, "'env' table should be ready"
        assert isinstance(db.table, anvil.tables.Table), "Expected to have a valid table"
        assert not db._missing_table_columns(), "Should not be missing any required columns"

    def test_missing_table(self):
        db = models.EnvDB('bad_table_name')
        assert not db._table_created(), "Table is not created"
        assert not db.is_ready, "should not be ready"
        assert db.table is None, "should not return a table"
        assert db._missing_table_columns() == db.required_columns, "Should require all of the columns"


class TestVariables:
    def test_empty(self):
        pass

    def test_available(self):
        pass

    def test_in_use(self):
        pass

    def test_all(self):
        pass