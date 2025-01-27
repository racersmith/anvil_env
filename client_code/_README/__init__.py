import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ._anvil_designer import _READMETemplate
class _README(_READMETemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
