import logging

import os
import mutagen

import multiprocessing

from sqlamp import tree_recursive_iterator

from decorator import decorator

from pylons import cache, config, request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from musicapp.lib.base import BaseController, render
from musicapp.model.meta import Session
from musicapp.model.tree import Node
from musicapp.model.fs import FileNode, DirectoryNode, RootNode, FSNode, clear_tree, walk_media
from musicapp.model.messages import FlashMessage, add_session_message

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
    q = Session.query(DirectoryNode).filter(c.root_node.mp.filter_descendants(and_self=True))
    
    c.directories = tree_recursive_iterator(q, Node.mp)
    return fn(*args, **kwargs)

def browse_fs_prelude(type_=FSNode):
    def internal(fn, self, path=""):
        if not validate_path(path):
            add_session_message("error", "Nice try...")
            redirect_to(controller="browse", action="directory", path="")

        c.node = Session.query(type_).filter(type_.webpath == path).first()
        return fn(self, path)
    return decorator(internal)

def regenerate_database(conn):
    # Generate our flash message.
    message = FlashMessage("info", "Music database is being "
                           "updated, please hold on...")
    Session.add(message)
    Session.commit()

    # Resume our parent "thread".
    conn.send(True)
    
    # Get our only root node.
    root = Session.query(RootNode).first()

    # Do the hard stuff!
    walk_media(media_path)
    
    if root:
        Session.delete(root)

    Session.delete(message)
    Session.commit()

class BrowseController(BaseController):

    def regenerate_database(self):
        forked, me = multiprocessing.Pipe()
        
        p = multiprocessing.Process(target=regenerate_database, args=(forked,))
        p.start()
        
        success = me.recv()
        
        if not success:
            abort(500, "Uh oh, something went wrong while spawning processes.")
            
        redirect_to(controller="browse", action="folder", path="")
        
    @browse_prelude
    @browse_fs_prelude(type_=DirectoryNode)
    def folder(self, path=""):
        
        if not validate_path(path):
            path = ""
        
        if c.node is None:
            add_message("error", "Directory could not be found")
            redirect_to(controller="browse", action="folder")
            
        # If the URL is a directory.
        elif c.node.is_directory:

            # Get our sort and order parameters from the request
            c.key = request.GET.get('sort', 'name')
            if c.key not in ('name', 'size', 'type'):
                c.key = 'name'
                
            c.reverse = request.GET.get('dir', 'desc') == 'asc'
                
            return render('/browse_folder.jinja')

    def music(self, path=""):
        pass
