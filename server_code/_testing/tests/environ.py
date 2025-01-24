from anvil.tables import app_tables
import anvil.tables

from anvil_testing import helpers

from ... import environ


class TestGet:
    _table = app_tables.env

    def test_error(self):
        with helpers.raises(LookupError):
            environ.get("non_existant_variable")

    def test_default(self):
        var = environ.get("missing_variable", None)
        assert var is None, f"expected var to be None got {var}"

    def test_existing(self):
        variable_name = "test_existing"
        variable_value = hash(variable_name)
        with helpers.temp_row(self._table, key=variable_name, value=variable_value):
            var = environ.get(variable_name)
            assert (
                var == variable_value
            ), f"Did not get the expected value {var=} != {variable_value=}"

    def test_existing_with_default(self):
        variable_name = "test_existing_with_default"
        variable_value = str(hash(variable_name))
        with helpers.temp_row(self._table, key=variable_name, value=variable_value):
            var = environ.get(variable_name, None)
            assert (
                var == variable_value
            ), f"Did not get the expected value {var=} != {variable_value=}"


class TestSet:
    _table = app_tables.env
    
    def test_set_new(self):
        variable_name = helpers.gen_str()
        variable_value = helpers.gen_int()
        with helpers.temp_writes():
            environ.set(variable_name, variable_value)
            var = environ.get(variable_name)
            assert var == variable_value, f"Did not get the expected value {var=} != {variable_value=}"

    def test_set_existing(self):
        variable_name = "test_set_existing"
        variable_value = 1234
        with helpers.temp_row(
            self._table, key=variable_name, value=str(hash(variable_name))
        ):
            environ.set(variable_name, variable_value)
            var = environ.get(variable_name)
            for row in self._table.search():
                print(f"{row['key']}: {row['value']}")
            assert var == variable_value, f"Did not get the expected value {var=} != {variable_value=}"
