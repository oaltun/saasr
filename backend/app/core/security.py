import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# compulsory fields. So we ensure their proper format using this function
def exp_sub_td(user_email:str):
    expire = datetime.utcnow() + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
    return expire, user_email, settings.TOKEN_EXPIRE_MINUTES


def create_access_token(*, data: dict):
    to_encode = data.copy()

    return jwt.encode(to_encode, settings.SAASR_TOKEN_SECRET_KEY, algorithm=settings.SAASR_TOKEN_ALGORITHM)
