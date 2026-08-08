from fastapi import APIRouter, UploadFile, Depends
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

    # check for code collision
    code = generate_short_code()

    # generate a unique code
    while check_db(code, db):
        code = generate_short_code()

    # path to store files at
    upload_dir = Path("./data/uploads")

    # create dir if it doesnt exist
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(file.filename).suffix
    # complete file path(relative) to the file
    destination = upload_dir / f"{code}{extension}"

    # copy file data in chunks in bytes so huge data is not loaded into RAM
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    uploaded_file = UploadedFile(short_code=code, original_filename=file.filename)

    db.add(uploaded_file)
    db.commit()

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
    return FileResponse(
        path= Path("./data/uploads/") / f"{code}{extension}",
        filename= file_record.original_filename,
    )