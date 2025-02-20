import anvil.tables

from anvil_testing import helpers

from ...environ import models, src


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


class TestSecret:
    def test_storage(self):
        name = helpers.gen_str()
        secret = models.Secret(name)
        with helpers.temp_writes():
            row = src.DB.table.add_row(key=name, value=secret)
            assert row['value'] is not None, "'value' should have something in there"
            assert models.Secret._is_secret(row['value']), f"{row['value']} should be seen as a secret"
        

class TestVariable:
    def test_simple(self):
        name = helpers.gen_str()
        default = models.NotSet
        variable = models.Variable(name, default=models.NotSet)
        assert variable.name == name, f"Variable name is wrong {variable.name=} != {name=}"
        assert variable.value == default, f"Variable value is wrong {variable.value=} != {default=}"
        assert variable.in_use is False, "Variable is not in use yet."

        value = helpers.gen_int()
        variable.value = value
        assert variable.value == value, f"Variable value is wrong {variable.value=} != {value=}"
        assert variable.in_use is True, "Variable is in use."

    def test_set_use(self):
        a = models.Variable('a', 'a')
        b = models.Variable('b', 'b')
        c = models.Variable('c', 'c')
        c_ = models.Variable('c', 'c')

        var_list = [a, b, c, c_]
        var_set = set(var_list)
        assert len(var_list) == 4
        assert len(var_set) == 3
        for var in var_list:
            assert var in var_set

    def test_string(self):
        name = 'variable_name'
        default = 'default_value'
        a = models.Variable(name, default)
        assert name in str(a)
        assert name in a.details
        assert default in a.details

        a.value = 1234
        assert '1234' in a.details


class TestVariables:
    def test_empty(self):
        VARIABLES = models.Variables()
        assert len(VARIABLES.in_use) == 0
        assert len(VARIABLES.available) == 0
        assert len(VARIABLES.all) == 0

    def test_available(self):
        VARIABLES = models.Variables()
        VARIABLES._register(models.Variable('test_var', None))
        VARIABLES._register(models.Variable('test_var', 10))
        assert len(VARIABLES.in_use) == 0
        assert len(VARIABLES.available) == 1
        assert len(VARIABLES.all) == 1
        assert 'test_var' in VARIABLES.available

    def test_in_use(self):
        VARIABLES = models.Variables()
        a = models.Variable('a', 10)
        a.value = 10

        b = models.Variable('b', 11)
        b.value = 110

        c = models.Variable('b', 12)
        c.value = 120
        
        VARIABLES._register(a)
        VARIABLES._register(b)
        VARIABLES._register(c)
        assert len(VARIABLES.in_use) == 2, f"Expected 2 in use variables {VARIABLES.in_use}"
        assert len(VARIABLES.available) == 0, f"Expected 0 available variables {VARIABLES.available}"
        assert len(VARIABLES.all) == 2, f"Expected 2 variables {VARIABLES.all}"
        assert a in VARIABLES.in_use, f"Expected to find {a} in {VARIABLES.in_use}"
        assert b in VARIABLES.in_use, f"Expected to find {b} in {VARIABLES.in_use}"

    def test_all(self):
        VARIABLES = models.Variables()

        a = models.Variable('a', 10)
        a.value = 10

        b = models.Variable('b', 11)
        b.value = 110

        c = models.Variable('c', 12)
        
        d = models.Variable('d', 12)
        
        VARIABLES._register(a)
        VARIABLES._register(b)
        VARIABLES._register(c)
        VARIABLES._register(d)

        assert len(VARIABLES.in_use) == 2
        assert len(VARIABLES.available) == 2
        assert len(VARIABLES.all) == 4
        assert a in VARIABLES.in_use
        assert b in VARIABLES.in_use
        assert c in VARIABLES.available
        assert d in VARIABLES.available
        for var in [a, b, c, d]:
            assert var in VARIABLES.all
        