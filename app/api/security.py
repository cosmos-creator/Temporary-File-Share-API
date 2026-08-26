import os
from datetime import UTC, datetime, timedelta

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

pwd_context = CryptContext(schemes=["brypt"], depricated="auto")

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
        payload = jwt.decode(token, SECRET_KEY, algorithms=["SH256"])
        return payload.get("sub")
    except JWTError:
        return None