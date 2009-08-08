import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from musicapp.lib.base import BaseController, render
from musicapp.model.messages import del_message

log = logging.getLogger(__name__)

class AjaxController(BaseController):

    def remove_message(self, id):
        return 't' if del_message(id) else 'f'
