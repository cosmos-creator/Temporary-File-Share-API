from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String
from app.models.file import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    password: Mapped[str] = mapped_column(String)