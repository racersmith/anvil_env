from anvil.tables import app_tables
from anvil import tables
from anvil import _AppInfo

from anvil_testing import helpers

from ... import environ
from ...environ import models, src


class _Mock:
    def __init__(self):
        # why the signature for envrionment uses 'description' but the object uses 'name' is beyond me... but here we are.
        self._published_environment = _AppInfo._Environment(
            description="Published", tags=[]
        )
        self._debug_environment = _AppInfo._Environment(
            description="Debug for abc@example.com", tags=["debug"]
        )
        self._unknown_environment = _AppInfo._Environment(
            description="Staging", tags=[]
        )
        self._environments_db = models.EnvDB("env")
        self._basic_db = models.EnvDB("basic_env")

    def enable_environments(self):
        src.DB = self._environments_db

    def disable_environments(self):
        src.DB = self._basic_db

    def debug(self):
        src.ENVIRONMENT = self._debug_environment

    def published(self):
        src.ENVIRONMENT = self._published_environment

    def unknown(self):
        src.ENVIRONMENT = self._unknown_environment


_mock = _Mock()


class TestResolveEnvironment:
    def test_direct_match(self):
        env = src.resolve_environment('A', {'A', 'B'})
        assert env == 'A'

        env = src.resolve_environment('B', {'A', 'B'})
        assert env == 'B'

        env = src.resolve_environment('B', {'A', 'B', 'BB'})
        assert env == 'B'

    def test_indirect_match(self):
        env = src.resolve_environment('B with extra', {'A', 'B', 'C'})
        assert env == 'B'

    def test_no_match(self):
        with helpers.raises(LookupError):
            env = src.resolve_environment('E', {'A', 'B', 'C'})

    def test_ambiguous_matching(self):
        with helpers.raises(LookupError):
            env = src.resolve_environment('A', {'A1', 'AA', 'B'})


class TestGet:
    def test_error(self):
        _mock.disable_environments()
        with helpers.raises(LookupError):
            environ.get("non_existant_variable")

    def test_default(self):
        _mock.disable_environments()
        default = "my default value"
        var = environ.get("missing_variable", default)
        assert var is default, f"expected var to be {None} got {var}"

    def test_existing(self):
        _mock.disable_environments()
        variable_name = "test_existing_ed5854bc"
        variable_value = hash(variable_name)
        with helpers.temp_row(
            environ.src.DB.table, key=variable_name, value=variable_value
        ):
            var = environ.get(variable_name)
            assert (
                var == variable_value
            ), f"Did not get the expected value {var=} != {variable_value=}"

    def test_existing_with_default(self):
        _mock.disable_environments()
        variable_name = "test_existing_with_default_380c2dde"
        variable_value = str(hash(variable_name))
        with helpers.temp_row(
            environ.src.DB.table, key=variable_name, value=variable_value
        ):
            var = environ.get(variable_name, None)
            assert (
                var == variable_value
            ), f"Did not get the expected value {var=} != {variable_value=}"

    def test_dev_and_prod_vars(self):
        _mock.enable_environments()
        _mock.debug()

        variable_name = "c6340ab7"

        dev_var = environ.get(variable_name, "default_value")
        assert (
            dev_var == "default_value"
        ), f"Didn't get the default value in dev mode: {dev_var}"

        _mock.published()
        assert (
            dev_var == "default_value"
        ), f"Didn't get the default value in prod mode: {dev_var}"

        with helpers.temp_writes():
            environ.set(
                variable_name, "development_value", environments=dict(Debug=True)
            )
            environ.set(
                variable_name, "production_value", environments=dict(Published=True)
            )

            _mock.debug()
            var = environ.get(variable_name, None)
            assert (
                var == "development_value"
            ), f"Did not get the expected value {var=} != development_value"

            _mock.published()
            var = environ.get(variable_name, None)
            assert (
                var == "production_value"
            ), f"Did not get the expected value {var=} != production_value"

    def test_overlapping_environments(self):
        _mock.enable_environments()

        variable_name = "test_overlapping_environments"
        with helpers.temp_writes():
            environ.set(
                variable_name,
                helpers.gen_int(),
                environments={"Debug": True, "Published": True},
            )
            environ.set(variable_name, helpers.gen_int(), environments={"Debug": True})
            with helpers.raises(tables.TableError):
                environ.get(variable_name)

    def test_default_environment(self):
        _mock.enable_environments()

        variable_name = "test_default_environment"
        with helpers.temp_writes():
            environ.set(
                variable_name,
                "PublishedValue",
                environments={"Published": True},
            )
            environ.set(variable_name, "DefaultValue")
            
            _mock.published()
            var = environ.get(variable_name)
            assert environ.get(variable_name) == "PublishedValue", f"Didn't get the expected value for published env: {var}"

            _mock.unknown()
            var = environ.get(variable_name)
            assert environ.get(variable_name) == "DefaultValue", f"Didn't get the expected value for unknown env: {var}"
            


class TestSet:
    # We will use this to temporarily override the dev mode state
    def test_set_new(self):
        _mock.disable_environments()

        variable_name = "5358d6b3"
        variable_value = helpers.gen_int()

        with helpers.temp_writes():
            environ.set(variable_name, variable_value)
            var = environ.get(variable_name)
            assert (
                var == variable_value
            ), f"Did not get the expected value {var=} != {variable_value=}"

    def test_not_implemented_error(self):
        # override the default database
        _mock.disable_environments()
        variable_name = "80257ac7"
        variable_value = 1234
        with helpers.temp_row(
            environ.DB.table, key=variable_name, value=helpers.gen_int()
        ):
            with helpers.raises(NotImplementedError):
                environ.set(variable_name, variable_value, environments={"Debug": True})

    def test_set_existing_development(self):
        variable_name = "2c950b27"
        variable_value = 1234
        _mock.enable_environments()
        with helpers.temp_writes():
            environ.set(variable_name, helpers.gen_int(), environments={"Debug": True})

            environ.set(variable_name, variable_value, environments={"Debug": True})
            environ.set(
                variable_name, variable_value + 1, environments={"Published": True}
            )

            _mock.debug()
            var = environ.get(variable_name)
            assert (
                var == variable_value
            ), f"Did not get the expected value {var=} != {variable_value=}"

            _mock.published()
            var = environ.get(variable_name)
            assert (
                var == variable_value + 1
            ), f"Did not get the expected value {var=} != {variable_value+1=}"

    def test_set_existing_non_development(self):
        _mock.disable_environments()
        _mock.debug()
        variable_name = "366cd7ee"
        variable_value = 1234
        with helpers.temp_row(
            environ.src.DB.table, key=variable_name, value=str(hash(variable_name))
        ):
            # with helpers.raises(NotImplementedError):
            #     environ.set(variable_name, variable_value)
            environ.set(variable_name, variable_value)
            var = environ.get(variable_name)
            assert (
                var == variable_value
            ), f"Did not get the expected value {var=} != {variable_value=}"
