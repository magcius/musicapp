import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from musicapp.lib.base import BaseController, render

log = logging.getLogger(__name__)

class LoginController(BaseController):

    def commit(self):
        # Return a rendered template
        #return render('/login.mako')
        # or, return a response
        pass
