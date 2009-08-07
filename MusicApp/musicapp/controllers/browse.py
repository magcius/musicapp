zimport logging

import os
import mutagen

from decorator import decorator

from pylons import cache, config, request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from musicapp.lib.base import BaseController, render
from musicapp.lib.helpers import add_message
from musicapp.model.meta import Session
from musicapp.model.fs import FileNode, DirectoryNode, RootNode, FSNode

log = logging.getLogger(__name__)

def validate_path(path):
    if path.startswith('..'):
        return False
    if path.startswith('%2e'):
        return False
    return True

media_path = os.path.abspath(config["media.path"])

@decorator
def browse_prelude(fn, *args, **kwargs):
    c.root_node = Session.query(RootNode).first()
    return fn(*args, **kwargs)

def browse_fs_prelude(type_=FSNode):
    def internal(self, fn, path=""):
        if not validate_path(path):
            add_message("error", "Nice try...")
            redirect_to(controller="browse", action="directory", path="")
            
        c.node = Session.query(type_).filter(type_.webpath == path).first()
        return fn(self, path)
    return decorator(internal)
    
class BrowseController(BaseController):

    def regenerate_database(self):
        tree.clear_tree()
        tree.walk_media(media_path)

    @browse_prelude
    @browse_fs_prelude(type_=DirectoryNode)
    def folder(self, path=""):
        
        if not validate_path(path):
            path = ""
        
        if c.node is None:
            add_message("error", "Directory could not be found")
            redirect_to(controller="browse", action="directory", path="")
            
        # If the URL is a directory.
        elif c.node.is_directory:
            
            c.key = request.GET.get('sort', 'name')
            if c.key not in ('name', 'size', 'type'):
                c.key = 'name'
            
            c.reverse = request.GET.get('dir', 'desc') == 'asc'
                
            return render('/browse_folder.jinja')

    def music(self, path=""):
        pass
