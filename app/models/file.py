from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

class UploadedFile(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(primary_key=True),
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    short_code: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable= True)
    downloads_remaining: Mapped[int | None] = mapped_column(Integer, nullable=True)