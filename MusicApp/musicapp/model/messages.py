
import sqlalchemy
import sqlalchemy.orm

from pylons import session

from musicapp.model.meta import metadata, Session

class FlashMessage(object):
    
    def __init__(self, type, message, user=None):
        self.type = type
        self.message = message
        self.user = user
    
messages_table = sqlalchemy.Table("messages", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("type", sqlalchemy.String),
    sqlalchemy.Column("message", sqlalchemy.String),
)

messages_mapper = sqlalchemy.orm.mapper(FlashMessage, messages_table)


def add_session_message(type, message):
    session.setdefault('messagetotal', 0)
    session['messagetotal'] += 1
    session.setdefault('messages', {})
    session['messages']['session_%d' % session['messagetotal']] = (type, message)
    session.save()

def del_message(id):
    if id.startswith("FlashMessage_"):
        id = id[len("FlashMessage_"):]
    if id.startswith("session_") and id in session['messages']:
        session['messages'].pop(id)
        return True
    elif id.startswith("db_"):
        q = Session.query(FlashMessage).filter(FlashMessage.id == int(id[len("db_"):]))
        if len(q) == 1:
            Session.delete(q.first())
            return True
    return False

def get_all_messages():
    m = {}
    if 'messages' in session:
        m.update(session['messages'])
    m.update(dict(("db_%d" % f.id, (f.type, f.message)) for f in Session.query(FlashMessage)))
    return m
