from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from dotenv import load_dotenv
import os

load_dotenv()

# SETTINGS
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# PASSWORD HASH
pwd_context = CryptContext(schemes=["bcrypt"],
                           deprecated="auto",
                           bcrypt__rounds=12)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Создать токен
def create_access_token(data: dict):
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({**data, "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)


# проверить токен
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Uncorrected token")


# хэширование паролей
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# проверка пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)