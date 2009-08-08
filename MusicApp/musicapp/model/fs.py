
import os
import operator

import sqlalchemy.orm
import sqlalchemy
import sqlamp

from musicapp.lib.helpers import pretty_size, pluralize
from musicapp.model import meta, tree

import logging

debug_count = 0

fsnode_table = sqlalchemy.Table('fsnode', meta.metadata,
    sqlalchemy.Column('node_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('node.id'), primary_key=True),
    sqlalchemy.Column('size', sqlalchemy.Integer),
    sqlalchemy.Column('webpath', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('localpath', sqlalchemy.String, nullable=True),
)

filenode_table = sqlalchemy.Table('filenode', meta.metadata,
    sqlalchemy.Column('fsnode_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('fsnode.node_id'), primary_key=True),
    sqlalchemy.Column('filetype', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('icon', sqlalchemy.String, nullable=False),
)

class FSNode(tree.Node):
    pass

class DirectoryNode(FSNode):
    icon = "folder"
    is_directory = True
    filetype = "Folder"
    
    def __init__(self, dirname):
        super(DirectoryNode, self).__init__(dirname)
        self.size = 0
        
    def add_child(self, child):
        child.parent = self
        
        child.webpath = u"%s/%s" % (unicode(self.webpath), unicode(child.name))
        child.localpath = os.path.join(self.localpath, child.name.encode('utf8'))
        
        self.size += 1
        return child

    @property
    def pretty_size(self):
        return "%d item%s" % pluralize(self.size)

    @property
    def files(self):
        return meta.Session.query(FileNode).filter(self.mp.filter_children())
    
    @property
    def directories(self):
        return meta.Session.query(DirectoryNode).filter(self.mp.filter_children())
    
    def sorted_files(self, key):
        return sorted(self.files, key=operator.attrgetter(key))
    
    def sorted_directories(self, key):
        return sorted(self.directories, key=operator.attrgetter(key))

    def sorted_children(self, key, reverse):
        print "getting children"
        children = (self.sorted_directories(key) + self.sorted_files(key))
        if reverse:
            children.reverse()
        return children

class RootNode(DirectoryNode):
    def __init__(self, localpath):
        super(RootNode, self).__init__("")
        self.webpath = ""
        self.localpath = localpath

class FileNode(FSNode):
    is_directory = False
    def __init__(self, filename):
        super(FileNode, self).__init__(filename)
        name = self.name.lower()
        if name.endswith((".jpg", ".gif", ".jpeg", ".png")):
            self.icon = "image"
            self.filetype = "Image file"
        elif name.endswith((".mp3", ".aac", ".mp4", ".m4a", ".ogg", ".flac", ".wav")):
            self.icon = "music"
            self.filetype = "Music file"
        else:
            self.icon = "file"
            self.filetype = "%s file" % os.path.splitext(filename)[1].strip(".").upper()
            
    @property
    def pretty_size(self):
        return pretty_size(self.size)

    def calculate_size(self):
        self.size = os.stat(self.localpath).st_size    

fsnode_mapper   = sqlalchemy.orm.mapper(FSNode, fsnode_table, inherits=tree.Node, polymorphic_identity='fsnode')
dirnode_mapper  = sqlalchemy.orm.mapper(DirectoryNode, inherits=FSNode, polymorphic_identity='dirnode')
rootnode_mapper = sqlalchemy.orm.mapper(RootNode, inherits=DirectoryNode, polymorphic_identity='rootnode')
filenode_mapper = sqlalchemy.orm.mapper(FileNode, filenode_table, inherits=FSNode, polymorphic_identity='filenode')

def clear_tree():
    for node in meta.Session.query(RootNode):
        meta.Session.delete(node)
    
def walk_media(media_path):
    # Create our root node.
    root = RootNode(media_path)
    
    # Create a directory map so we can find the parent.
    dirmap = {media_path: root}

    # Walk the directory tree
    for path, dirnames, files in os.walk(media_path):
        
        if path == media_path:
            continue
        
        # Find our parent path and direectory name
        parent_path, name = os.path.split(path)
        
        parent = dirmap[parent_path]
        node = parent.add_child(DirectoryNode(name.decode('utf8')))
        dirmap[node.localpath] = node

        #meta.Session.add(node)
        
        # Create the FileNodes
        for filename in files:
            filenode = node.add_child(FileNode(filename.decode('utf8')))
            filenode.calculate_size()

    logger = logging.getLogger("sqlalchemy")
    level = logger.level
    logger.setLevel(logging.WARN)
    
    # Save our data in the database.
    meta.Session.add(root)
    meta.Session.commit()

    # And revert back to what it was before.
    logger.setLevel(level)
    
    return root
