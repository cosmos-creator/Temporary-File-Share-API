from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase

db_url = "postgresql://tfs:tfs@db:5432/tfs"

engine = create_engine(db_url)

# tells that any class inheriting from this is a db table
class Base(DeclarativeBase):
    pass

def create_db_tables():
    from app.models.file import UploadedFile
    Base.metadata.create_all(engine)