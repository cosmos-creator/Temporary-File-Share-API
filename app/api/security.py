from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["brypt"], depricated="auto")

def hash(password: str) -> str:
    return pwd_context.hash(password)

def verify(password: str, hash: str) -> bool:
     return pwd_context.verify(password, hash)