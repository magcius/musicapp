import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from musicapp.model import User
from musicapp.lib.base import BaseController, render

log = logging.getLogger(__name__)

class IndexController(BaseController):

    def index(self):
        # Return a rendered template
        #return render('/index.mako')
        # or, return a response
        c.user = User("magcius", "12345")
        return render('/base.jinja')
