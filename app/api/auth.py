from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.security import create_jwt, hash, verify
from app.db import engine
from app.models.user import User

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
    new_user = User(username=info.username, password=pass_hash)

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


@router.post("/login")
async def login(info: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    stmnt = select(User).where(User.username == info.username)
    user = db.execute(stmnt).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401, detail="username or password incorrect")

    if not verify(info.password, user.password):
        raise HTTPException(
            status_code=401, detail="username or password incorrect")

    token = create_jwt(data={"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer"
    }
