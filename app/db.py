from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase

sqlite_file = "db.sqlite3"
sqlite_url = f"sqlite:///./{sqlite_file}"

engine = create_engine(sqlite_url)

# tells that any class inheriting from this is a db table
class Base(DeclarativeBase):
    pass

def create_db_tables():
    from app.models.file import UploadedFile
    Base.metadata.create_all(engine)