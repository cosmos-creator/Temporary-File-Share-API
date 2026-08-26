from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.models.user import User
from app.db import engine
from pydantic import BaseModel
from app.api.security import hash, verify

def get_db():
    with Session(engine) as session:
        yield session

class UserInfo(BaseModel):
    username: str
    password: str

router = APIRouter()

@router.post("/register")
async def register(info: UserInfo, db: Session = Depends(get_db)):
    pass_hash = hash(info.password)
    new_user = User(username=info.username, password= pass_hash)

    try:
        db.add(new_user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="username already taken")

    return {
        "username": info.username,
        "id": new_user.id
    }