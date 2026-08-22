from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer
from app.db import Base
from datetime import datetime

class UploadedFile(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(primary_key=True)
    short_code: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable= True)
    downloads_remaining: Mapped[int | None] = mapped_column(Integer, nullable=True)