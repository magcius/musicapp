b"""The application's model objects"""
import sqlalchemy as sa
from sqlalchemy import orm

from musicapp.model import meta, tree, fs

from random import choice
from hashlib import sha512

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    ## Reflected tables must be defined and mapped here
    #global reflected_table
    #reflected_table = sa.Table("Reflected", meta.metadata, autoload=True,
    #                           autoload_with=engine)
    #orm.mapper(Reflected, reflected_table)
    #
    meta.Session.configure(bind=engine)
    meta.engine = engine


## Non-reflected tables may be defined and mapped at module level
# user_table = sa.Table("user", meta.metadata,
#          sa.Column("id", sa.types.Integer, primary_key=True),
#          sa.Column("username", sa.types.String(255), nullable=False),
#          sa.Column("password", sa.types.String(128), nullable=False),
#          sa.Column("salt", sa.types.String(15), nullable=False),
# )

# salt_choices = [chr(c) for c in xrange(32, 128)]

# def generate_salt():
#     return ''.join(random.choice(salt_choices) for i in xrange(15))

# class User(object):
#     def __init__(self, username, password, salt=""):
#         self.username = username
#         self.password = password
#         self.salt = salt
    
#     def hash_password(self, password):
#         return sha512(sha512(password).hexdigest() + self.salt).hexdigest()
    
#     def check_password(self, incoming_pass):
#         return self.password == self.hash_password(incoming_pass)

# orm.mapper(User, user_table)

