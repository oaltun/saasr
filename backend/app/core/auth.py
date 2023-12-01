from typing import Union, cast
import uuid
import jwt
from pydantic import EmailStr
from app.core.error import error_detail

from fastapi import Depends,  status, HTTPException
from jwt import PyJWTError

from app.user import model, schema
from app.core import session
from app.user.crud import get_user_by_email, create_user
from app.core import security
from app.config import settings

def raise_credentials_exception_401(code):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=error_detail(code),
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_user(
    db=Depends(session.get_db), token: str = Depends(security.oauth2_scheme)
):
    # credentials_exception = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="Could not validate credentials",
    #     headers={"WWW-Authenticate": "Bearer"},
    # )
    try:
        payload = jwt.decode(
            token, settings.SAASR_TOKEN_SECRET_KEY, algorithms=[settings.SAASR_TOKEN_ALGORITHM]
        )
        email: Union[EmailStr,None] = payload.get("sub")
        if email is None:
            raise_credentials_exception_401("INVALID_CREDENTIALS_I")
        permissions: Union[str,None] = payload.get("prm")
        if permissions is None:
            raise_credentials_exception_401("INVALID_CREDENTIALS_I")

        token_data = schema.TokenRequired(sub=email, prm=permissions)

    except PyJWTError:
        raise_credentials_exception_401("INVALID_CREDENTIALS_II")

    user = get_user_by_email(db, token_data.sub)

    if user is None:
        raise_credentials_exception_401("INVALID_CREDENTIALS_III")

    return user


async def get_current_active_user_or_400(
    current_user: model.User = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=400, 
            detail=error_detail("USER_INACTIVE")
        )
    return current_user


async def get_current_active_superuser_or_403(
    current_user: model.User = Depends(get_current_user),
) -> model.User:
    if not current_user.is_superuser:
        print("(847d90ae)")
        raise HTTPException(
            status_code=403, detail=error_detail("USER_NOT_SUPERUSER")
        )
    return current_user


def authenticate_user(db, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    hash:str = cast(str,user.hashed_password)
    if not security.verify_password(password, hash): 
        return False
    return user



def create_new_user_or_409(db, email: str, password: str):
    user = get_user_by_email(db, email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_detail("USER_ALREADY_IN_DB"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    new_user = create_user(
        db,
        schema.UserCreate(
            email=email,
            password=password,
            is_active=True,
            is_verified=False,
            is_superuser=False,
        ),
    )

    return new_user
