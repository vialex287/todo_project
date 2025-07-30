from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

from app.core.config import settings
from app.dependencies import get_async_db
from app.models import User

load_dotenv()

# SETTINGS
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# PASSWORD HASH
pwd_context = CryptContext(schemes=["pbkdf2_sha256"],
                           deprecated="auto",
                           bcrypt__rounds=12)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# Создать токен
def create_access_token(data: dict):
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({**data, "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)


# проверить токен отдельно
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Uncorrected token")

# проверка токена
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_async_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        query = await db.execute(select(User).where(User.email == email))
        user = query.scalars().first()

        if user is None:
            raise HTTPException(status_code=401, detail="User is not found")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="User is not active")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# хэширование паролей
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# проверка пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

