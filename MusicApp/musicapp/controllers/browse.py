import logging

import os
import operator
import mutagen

from pylons import cache, config, request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from musicapp.lib.base import BaseController, render
from musicapp.lib.helpers import add_message, pretty_size, pluralize

log = logging.getLogger(__name__)

def validate_path(path):
    if path.startswith('..'):
        return False
    if path.startswith('%2e'):
        return False
    return True

media_path = os.path.abspath(config["media.path"])

class Node(object):
    def __init__(self, name):
        self.name = unicode(name)

    def __unicode__(self):
        return u'<%s (path="%s")>' % (self.__class__.__name__, self.localpath)

    __repr__ = __unicode__
    
class DirectoryNode(Node):
    icon = "folder"
    is_directory = True
    type = "Folder"
    
    def __init__(self, dirname):
        super(DirectoryNode, self).__init__(dirname)
        self.files = []
        self.directories = []
        self.size = 0
        
    def add_child(self, child):
        child.parent = self
        
        child.webpath = u"%s/%s" % (unicode(self.webpath), unicode(child.name))
        child.localpath = os.path.join(self.localpath, child.name.encode('utf8'))
        
        if child.is_directory:
            self.directories.append(child)
        else:
            self.files.append(child)
        self.size += 1
        return child

    @property
    def pretty_size(self):
        return "%d item%s" % pluralize(self.size)
    
    def sorted_files(self, key):
        return sorted(self.files, key=operator.attrgetter(key))
    
    def sorted_directories(self, key):
        return sorted(self.directories, key=operator.attrgetter(key))

    def sorted_children(self, key=None, reverse=None):
        if key is None:
            key = request.GET.get('sort', 'name')
            if key not in ('name', 'size', 'type'):
                key = 'name'
        if reverse is None:
            reverse = request.GET.get('dir', 'desc') == 'asc'
        children = (self.sorted_directories(key) + self.sorted_files(key))
        if reverse:
            print "reversing"
            children.reverse()
        return children

class RootNode(DirectoryNode):
    def __init__(self):
        super(RootNode, self).__init__("")
        self.webpath = ""
        self.localpath = media_path

class FileNode(Node):
    is_directory = False
    def __init__(self, filename):
        super(FileNode, self).__init__(filename)
        if self.name.endswith((".jpg", ".gif", ".jpeg", ".png")):
            self.icon = "image"
            self.type = "Image file"
        elif self.name.endswith((".mp3", ".aac", ".mp4", ".m4a", ".ogg", ".flac", ".wav")):
            self.icon = "music"
            self.type = "Music file"
        else:
            self.icon = "file"
            self.type = "%s file" % os.path.splitext(filename)[1].strip(".").upper()
            
    @property
    def pretty_size(self):
        return pretty_size(self.size)

    def calculate_size(self):
        self.size = os.stat(self.localpath).st_size

            
def create_dir_items():
    # Create our root node.
    root = RootNode()
    
    # Create a directory map so we can find the parent.
    dirmap = {media_path: root}

    # Walk the directory tree
    for path, dirnames, files in os.walk(media_path):
        
        if path == media_path:
            continue
        
        # Find our parent path and direectory name
        parent_path, name = os.path.split(path)
        
        parent = dirmap[parent_path]
        node = DirectoryNode(name.decode('utf8'))
        parent.add_child(node)
        dirmap[node.localpath] = node
        
        # Create the FileNodes
        for filename in files:
            filenode = node.add_child(FileNode(filename.decode('utf8')))
            filenode.calculate_size()

    return dirmap, root

media_cache = cache.get_cache('media', type='file')
dirmap, root_node = media_cache.get_value('directory', createfunc=create_dir_items)

class BrowseController(BaseController):
    
    def reset_cache(self):
        media_cache['temp'] = 1
        media_cache.clear()
        add_message("info", "Cache Cleared")
        redirect_to(controller="browse", action="directory", _code=301)
    
    def directory(self, path=""):
        if not validate_path(path):
            path = ""
        
        c.root_node = root_node
        fullpath = os.path.abspath(os.path.join(media_path, path))

        # If the URL is a directory.
        if os.path.isdir(fullpath):
            c.node = dirmap[fullpath]
            return render('/browse_folder.jinja')
        
        # If the URL is a file.
        elif os.path.isfile(fullpath):
            # Try to read it.
            metadata = mutagen.File(fullpath, easy=True)
            if metadata is not None:
                c.artist = metadata['artist'][0]
                c.album  = metadata['album'][0]
                c.title  = metadata['title'][0]
                return render('/browse_file_music.jinja')
            
        else:
            add_message("error", "Directory could not be found")
            redirect_to(controller="browse", action="directory", path="")
