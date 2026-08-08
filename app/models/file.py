from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from app.db import Base

class UploadedFile(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(primary_key=True)
    short_code: Mapped[str] = mapped_column(String(12), unique=True)
    original_filename: Mapped[str] = mapped_column(String(255))