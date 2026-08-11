from fastapi import APIRouter, UploadFile, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from pathlib import Path
from app.db import engine
from app.models.file import UploadedFile
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
    
router = APIRouter()

@router.get("/ping")
async def ping():
    return {"ping":"pong"}

@router.post("/uploadfile/")
def upload(file: UploadFile, db: Session = Depends(get_db)):

    # check if empty file
    if file.size == 0:
        raise HTTPException(status_code=400, detail="Rmpty file not allowed.")
    
    # check if file is too large (compared in BYTES)
    GB_IN_BYTES = 1073741824
    if file.size > (2 * GB_IN_BYTES):
        raise HTTPException(status_code=413, detail="File size exceeds 2GB.")

    # check for code collision
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
    
    uploaded_file = UploadedFile(short_code=code, original_filename=file.filename)

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
        "saved_to": str(destination)
    }

@router.get("/{code}")
async def download(code: str, db: Session = Depends(get_db)):
    statement = select(UploadedFile).where(UploadedFile.short_code == code)
    file_record = db.execute(statement).scalar_one_or_none()

    extension = Path(file_record.original_filename).suffix

    path= Path("./data/uploads/") / f"{code}{extension}"
    filename= file_record.original_filename,

    if file_record is None:
        raise HTTPException(status_code=404, detail="File not found")

    if not path.exists():
        db.delete(file_record)
        db.commit()
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=path,
        filename=filename
    )