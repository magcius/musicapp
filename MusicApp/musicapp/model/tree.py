
import os
import operator

import sqlalchemy.orm
import sqlamp

from musicapp.lib.helpers import pretty_size, pluralize
from musicapp.model import meta

node_table = sqlalchemy.Table('node', meta.metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('type', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('name', sqlalchemy.String),
    sqlalchemy.Column('parent_id', sqlalchemy.ForeignKey('node.id')),
)
                              
class Node(object):
    mp = sqlamp.MPManager(node_table, node_table.c.id, node_table.c.parent_id)
    
    def __init__(self, name, path=None, parent=None):
        self.name = name
        self.path = path
        self.parent = parent
    
    def __unicode__(self):
        return u"<%s %r>" % (self.__class__.__name__, self.name)

    __repr__ = __unicode__

    def __getitem__(self, name):
        try:
            return self.children[name] # allow node[0] for indexing
        except TypeError:
            return [child for child in self.children if child.name == name][0] # allow node[name] for map-like access

    def __setitem__(self, name, node):
        assert isinstance(node, Node)
        if isinstance(name, basestring):
            node.name = node
            self.children.append(node)
        else:
            self.children[name] = node

node_mapper = sqlalchemy.orm.mapper(
    Node, node_table,
    extension=[Node.mp.mapper_extension],
    polymorphic_on=node_table.c.type,
    polymorphic_identity='node',
    properties=dict(
        parent=sqlalchemy.orm.relation(Node,
                                       remote_side=[node_table.c.id],
                                       backref=sqlalchemy.orm.backref('children', cascade='all, delete'),
                                       cascade='all, delete')
    )
)
