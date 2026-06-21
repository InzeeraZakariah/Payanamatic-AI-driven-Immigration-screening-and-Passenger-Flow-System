from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = ("postgresql://postgres:7869@localhost/Payanamatic")

engine = create_engine(DATABASE_URL) # make a connection to the db

sessionLocal = sessionmaker( #  A factory that generates Session objects. Sessions are used to interact with the database (query, insert, update, delete).
    autocommit=False,
    autoflush = False,
    bind = engine
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()