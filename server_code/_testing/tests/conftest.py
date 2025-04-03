from anvil import _AppInfo

from ...environ import models, src


class _Mock:
    def __init__(self):
        # why the signature for environment uses 'description' but the object uses 'name' is beyond me... but here we are.
        self._environments_db = models.EnvDB("env")
        self._basic_db = models.EnvDB("basic_env")

    def enable_environments(self):
        src.DB = self._environments_db

    def disable_environments(self):
        src.DB = self._basic_db

    def debug(self, user='abc'):
        src.ENVIRONMENT._environment = _AppInfo._Environment(
            description=f"Debug for {user}@example.com", tags=["debug"]
        )

    def published(self):
        src.ENVIRONMENT._environment = _AppInfo._Environment(
            description="Published", tags=[]
        )

    def staging(self):
        src.ENVIRONMENT._environment = _AppInfo._Environment(
            description="Staging", tags=[]
        )


_mock = _Mock()
