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
        VARIABLES = models.Variables()
        assert len(VARIABLES.in_use) == 0
        assert len(VARIABLES.available) == 0
        assert len(VARIABLES.all) == 0

    def test_available(self):
        VARIABLES = models.Variables()
        VARIABLES._register_available('test_var')
        VARIABLES._register_available('test_var')
        assert len(VARIABLES.in_use) == 0
        assert len(VARIABLES.available) == 1
        assert len(VARIABLES.all) == 1
        assert 'test_var' in VARIABLES.available
        

    def test_in_use(self):
        VARIABLES = models.Variables()
        VARIABLES._register_in_use('in_use_var')
        VARIABLES._register_in_use('in_use_var_2')
        VARIABLES._register_in_use('in_use_var_2')
        assert len(VARIABLES.in_use) == 2
        assert len(VARIABLES.available) == 0
        assert len(VARIABLES.all) == 2
        assert 'in_use_var' in VARIABLES.in_use
        assert 'in_use_var_2' in VARIABLES.in_use

    def test_all(self):
        VARIABLES = models.Variables()
        VARIABLES._register_in_use('in_use_var')
        VARIABLES._register_in_use('in_use_var_2')
        VARIABLES._register_available('test_var')

        VARIABLES._register_in_use('in_use_var')
        VARIABLES._register_available('test_var')
        assert len(VARIABLES.in_use) == 2
        assert len(VARIABLES.available) == 1
        assert len(VARIABLES.all) == 3
        assert 'test_var' in VARIABLES.available
        assert 'in_use_var' in VARIABLES.in_use
        assert 'in_use_var_2' in VARIABLES.in_use