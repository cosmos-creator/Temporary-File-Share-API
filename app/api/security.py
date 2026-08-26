import os
from datetime import UTC, datetime, timedelta

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import engine
from app.models.user import User

load_dotenv()

oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = os.getenv("SECRET_KEY")

pwd_context = CryptContext(schemes=["bcrypt"])


def get_db():
    with Session(engine) as session:
        yield session

def get_current_user(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):
    username = verify_jwt(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user

def hash(password: str) -> str:
    return pwd_context.hash(password)

def verify(password: str, hash: str) -> bool:
    return pwd_context.verify(password, hash)

def create_jwt(data: dict, expires_at: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_at
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, "HS256")

def verify_jwt(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except JWTError:
        return None