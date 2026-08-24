from fastapi import APIRouter, UploadFile, Depends, HTTPException, Request, Form
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from pathlib import Path
from app.db import engine
from app.models.file import UploadedFile
from datetime import datetime, timedelta, UTC
from enum import Enum
import shutil
import uuid


def get_db():
    with Session(engine) as session:
        yield session

def generate_short_code(length: int = 8):
    return uuid.uuid4().hex[:length]

def check_db(code: str, db: Session):
    statement = select(UploadedFile).where(UploadedFile.short_code == code)
    result = db.execute(statement).scalar_one_or_none()
    # F - if not found(None is returned)
    return result is not None 

def decrement_limit(file_record: UploadedFile, db: Session):
    # do not block downloads
    if file_record.downloads_remaining is None:
        # shouldnt be blocked
        return
    # block downloads
    if file_record.downloads_remaining == 0:
        raise HTTPException(status_code=404, detail="File not found")
    
    # decrement
    file_record.downloads_remaining -= 1
    db.commit()

class ExpiryOption(Enum):
    one_hour = "1h"
    one_day = "1d"
    one_week = "1w"
    never = "never"

router = APIRouter()

@router.get("/ping")
async def ping():
    return {"ping":"pong"}

@router.post("/uploadfile/")
async def upload(request: Request, file: UploadFile, download_limit: int | None = Form(default=5, description="number of times file can be downloaded"), expiry: ExpiryOption = Form(ExpiryOption.one_day), db: Session = Depends(get_db)):

    expiry_map = {
        ExpiryOption.one_hour: timedelta(hours=1),
        ExpiryOption.one_day: timedelta(days=1),
        ExpiryOption.one_week: timedelta(weeks=1),
        ExpiryOption.never: None,
    }
    delta = expiry_map[expiry]
    GB_IN_BYTES = 1073741824
    content_length = request.headers.get("content-length")

    if content_length and int(content_length) > GB_IN_BYTES * 2:
        raise HTTPException(status_code=413, detail="File size exceeds 2GB.")

    # check if empty file
    if file.size == 0:
        raise HTTPException(status_code=400, detail="Empty file not allowed.")
    
    # check if file is too large (compared in BYTES)
    if file.size > (2 * GB_IN_BYTES):
        raise HTTPException(status_code=413, detail="File size exceeds 2GB.")

    # create an initial code
    code = generate_short_code()

    # generate a unique code
    while check_db(code, db):
        code = generate_short_code()

    # path to store files at
    upload_dir = Path("./data/uploads")

    try:
        # create dir if it doesnt exist
        upload_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        raise HTTPException(status_code=500, detail="Failed to prepare upload directory")

    # get file extension
    extension = Path(file.filename).suffix

    # complete file path(relative) to the file
    destination = upload_dir / f"{code}{extension}"

    try:
        # copy file data in chunks in bytes so huge data is not loaded into RAM
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save file")
    
    uploaded_file = UploadedFile(short_code=code, 
                                original_filename=file.filename,
                                expires_at= datetime.now(UTC) + delta if delta else None,
                                downloads_remaining= download_limit
                                )

    try:
        db.add(uploaded_file)
        db.commit()
    except Exception:
        destination.unlink(missing_ok=True) # remove orphaned file on disk
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to commit to DB.")
    
    return {
        "filename": file.filename,
        "short_code": code,
        "saved_to": str(destination),
        "valid_till": uploaded_file.expires_at,
        "submitted_at": datetime.now(UTC)
    }

@router.get("/{code}")
async def download(code: str, db: Session = Depends(get_db)):
    statement = select(UploadedFile).where(UploadedFile.short_code == code)
    file_record = db.execute(statement).scalar_one_or_none()

    if file_record is None:
        raise HTTPException(status_code=404, detail="File not found")

    decrement_limit(file_record, db)

    if file_record.expires_at and file_record.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=404, detail="File not found")

    extension = Path(file_record.original_filename).suffix

    path= Path("./data/uploads/") / f"{code}{extension}"
    filename= file_record.original_filename


    if not path.exists():
        db.delete(file_record)
        db.commit()
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=path,
        filename=filename
    )