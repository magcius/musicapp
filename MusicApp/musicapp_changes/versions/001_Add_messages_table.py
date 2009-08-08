from sqlalchemy import *
from migrate import *

meta = MetaData(migrate_engine)
messages_table = Table("messages", meta,
    Column("id", Integer, primary_key=True),
    Column("type", String),
    Column("message", String),
)

def upgrade():
    messages_table.create()
    pass

def downgrade():
    messages_table.drop()
    pass
