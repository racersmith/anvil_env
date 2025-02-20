from anvil import _AppInfo

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
        self._staging = _AppInfo._Environment(
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

    def staging(self):
        src.ENVIRONMENT = self._staging


_mock = _Mock()
