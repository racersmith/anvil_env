from anvil.tables import app_tables

from anvil_testing import helpers

from ... import environ


class TestGet:
    _table = app_tables.env

    def test_error(self):
        with helpers.raises(LookupError):
            environ.get("non_existant_variable")

    def test_default(self):
        default = 'my default value'
        var = environ.get("missing_variable", default)
        assert var is default, f"expected var to be {None} got {var}"

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
        with helpers.temp_row(self._table, key=variable_name, value=variable_value, development=environ.src.DEVELOPMENT_MODE):
            var = environ.get(variable_name, None)
            assert (
                var == variable_value
            ), f"Did not get the expected value {var=} != {variable_value=}"

    def test_dev_and_prod_vars(self):
        environ.src.DEVELOPMENT_MODE = True
        variable_name = helpers.gen_str()
        
        dev_var = environ.get(variable_name, 'default_value')
        assert dev_var == 'default_value', f"Didn't get the default value in dev mode: {dev_var}"
        
        environ.src.DEVELOPMENT_MODE = False
        assert dev_var == 'default_value', f"Didn't get the default value in prod mode: {dev_var}"

        environ.src.DEVELOPMENT_MODE = True
        with helpers.temp_writes():
            environ.set(variable_name, 'development_value', development=True)
            environ.set(variable_name, 'production_value', development=False)
            
            environ.src.DEVELOPMENT_MODE = True
            var = environ.get(variable_name, None)
            assert var == 'development_value', f"Did not get the expected value {var=} != development_value"

            environ.src.DEVELOPMENT_MODE = False
            var = environ.get(variable_name, None)
            assert var == 'production_value', f"Did not get the expected value {var=} != production_value"
            


class TestSet:
    # We will use this to temporarily override the dev mode state
    dev_mode = bool(environ.DEVELOPMENT_MODE)
    
    def test_set_new(self):
        variable_name = helpers.gen_str()
        variable_value = helpers.gen_int()
        environ.src.DB = environ.src.models.EnvDB('env')
        with helpers.temp_writes():
            environ.set(variable_name, variable_value)
            var = environ.get(variable_name)
            assert var == variable_value, f"Did not get the expected value {var=} != {variable_value=}"

    def test_not_implemented_error(self):
        # override the default database
        environ.src.DB = environ.src.models.EnvDB('basic_env')
        variable_name = "test_set_existing"
        variable_value = 1234
        with helpers.temp_row(
            environ.DB.table, key=variable_name, value=helpers.gen_int(), development=environ.DEVELOPMENT_MODE
        ):
            with helpers.raises(NotImplementedError):
                environ.set(variable_name, variable_value, development=environ.DEVELOPMENT_MODE)

    def test_set_existing_development(self):
        variable_name = "test_set_existing"
        variable_value = 1234
        environ.src.DB = environ.src.models.EnvDB('env')
        with helpers.temp_row(
            environ.DB.table, key=variable_name, value=helpers.gen_int(), development=True):
            
            environ.set(variable_name, variable_value, development=True)
            environ.set(variable_name, variable_value + 1, development=False)

            environ.src.DEVELOPMENT_MODE = True
            var = environ.get(variable_name)
            assert var == variable_value, f"Did not get the expected value {var=} != {variable_value=}"

            environ.src.DEVELOPMENT_MODE = False
            var = environ.get(variable_name)
            assert var == variable_value + 1, f"Did not get the expected value {var=} != {variable_value+1=}"
            environ.src.DEVELOPMENT_MODE = self.dev_mode

    def test_set_existing_non_development(self):
        environ.src.DB = environ.src.models.EnvDB('basic_env')
        variable_name = "test_set_existing"
        variable_value = 1234
        with helpers.temp_row(
            environ.DB.table, key=variable_name, value=str(hash(variable_name))):
            with helpers.raises(NotImplementedError):
                environ.set(variable_name, variable_value)
            var = environ.get(variable_name)
            assert var == variable_value, f"Did not get the expected value {var=} != {variable_value=}"
