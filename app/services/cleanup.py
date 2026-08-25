from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from pathlib import Path
from app.db import engine
from app.models.file import UploadedFile

def cleanUp():
    with Session(engine) as session:
        stmnt = select(UploadedFile).where(
            or_(
                UploadedFile.downloads_remaining == 0,
                # UploadedFile.expires_at < datetime.now(UTC)
                UploadedFile.expires_at < datetime.utcnow()
            )
        )
        
        result = session.execute(stmnt).scalars().all()

        for file in result:
            session.delete(file)
        
        upload_dir = Path("./data/uploads")

        for file in result:
            # complete filename on disk
            name = file.short_code + Path(file.original_filename).suffix
            file_path = upload_dir / name
            # no need to wrap in try block as it is safe automatically
            file_path.unlink(missing_ok=True)

        session.commit()


scheduler = BackgroundScheduler()
scheduler.add_job(cleanUp, "interval", minutes=1)