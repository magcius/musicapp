
import logging
from musicapp.lib.base import BaseController, render
from musicapp import model
from musicapp import forms
from musicapp.model import meta
from formalchemy.ext.pylons.admin import FormAlchemyAdminController

log = logging.getLogger(__name__)

class AdminController(BaseController):
    model = model # where your SQLAlchemy mappers are
    forms = forms # module containing FormAlchemy fieldsets definitions
    def Session(self): # Session factory
        return meta.Session

AdminController = FormAlchemyAdminController(AdminController)
