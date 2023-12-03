import secrets
from typing import Literal, Union, cast
from app.core.crud import raise_if
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from app.core.schema import ErrorDetail

from pydantic import BaseModel

from app.user.crud import (
    check_password_valid,
    get_normalized_email_or_406,
    get_valid_user_secret,
    get_valid_user_secret_by_user,
    send_email_verification_or_424,
)
from app.user.model import User, UserSecret
from app.user.schema import Permissions, TokenOutData, UserEdit, UserOut, AccessToken
from app.team.util import get_participation_count, get_invitation_count
from app.core.error import error_detail, err
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException,
    # BackgroundTasks,
)
from datetime import timedelta

from pydantic import BaseModel, EmailStr


from app.core.session import get_db
from sqlalchemy.orm import Session
from sqlalchemy import Column, func

from app.core import security
from app.core.auth import (
    authenticate_user,
    create_new_user_or_409,
)
from app.config import settings
from password_validator import PasswordValidator  # type: ignore
from app.core.mail import send_mail_or_424
from app.user import html


auth_router = r = APIRouter()


@r.post(
    "/token",
    response_model=AccessToken,
    responses={
        401: {"model": ErrorDetail},
        406: {"model": ErrorDetail},
    },
)
async def login(db=Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    email = get_normalized_email_or_406(form_data.username)
    if not email:
        print("(b3d1)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail("EMAIL_INVALID_III"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = authenticate_user(db, email, form_data.password)
    if not user:
        print("(59b0)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail("USERNAME_OR_PASSWORD_INCORRECT"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # TODO: uncomment this part after email sending is solved.
    # superusers do not need email verification. But others do need it.
    # if (not user.is_verified) and (not user.is_superuser):
    #     print("(4128)")
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="User email is not verified",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )

    if not user.is_active:
        print("(8d01)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail("USER_INACTIVE_II"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_superuser:
        prm = "admin"
    else:
        prm = "user"
    permissions: Permissions = Permissions(prm=prm)  # just a check

    exp, sub, td = security.exp_sub_td(user.email)

    data = TokenOutData(  # just a check
        prm=permissions.prm,
        uid=str(user.id),
        td=td,  # time delta, or how many minutes token is valid
        ia=1 if user.is_active else 0,
        isu=1 if user.is_superuser else 0,
        iv=1 if user.is_verified else 0,
        pc=get_participation_count(user.id, db),
        ic=get_invitation_count(user.email, db),
        exp=exp,  # compulsory field. do not remove
        sub=sub,  # compulsory field. do not remove
    )

    access_token = security.create_access_token(data=data.dict())

    return {"access_token": access_token, "token_type": "bearer"}


class EmailVerificationRequestPayload(BaseModel):
    email: str


## In order to make it hard for malicious users to guess whether emails exist in
# our database, we always return 202 accepted.
@r.post(
    "/verify_request",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        424: {"model": ErrorDetail},
    },
)
async def verify_request(
    payload: EmailVerificationRequestPayload,
    # background_tasks: BackgroundTasks,
    db=Depends(get_db),
):
    message = send_email_verification_or_424(payload, db)

    if settings.SAASR_DEBUG:
        return {"message": message}
    else:
        return {"detail": "Message sent"}


@r.post(
    "/signup",
    response_model=UserOut,
    responses={
        400: {"model": ErrorDetail},
        409: {"model": ErrorDetail},
    },
    description="username is an email. password require minimum 8,"
    + " maximum 100 characters, needs uppercase and lowercase"
    + "letters, digits and symbols. password can not have spaces",
)
async def signup(
    db=Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    print("At sign up.")
    valid_username = get_normalized_email_or_406(form_data.username)
    if not valid_username:
        print("(debb)")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail("EMAIL_INVALID_II"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    password_is_valid = check_password_valid(form_data.password)
    if not password_is_valid:
        print("(ebb3)")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail("PASSWORD_INVALID"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    print("bsdf")
    user = create_new_user_or_409(db, valid_username, form_data.password)
    print("zlj8")
    if not user.is_verified:
        sent = send_email_verification_or_424(
            payload=EmailVerificationRequestPayload(email=user.email), db=db
        )
    print("u8769")
    return user


class EmailVerifyPayload(BaseModel):
    hash: str


class EmailVerifyReturn(BaseModel):
    detail: Literal["verified",]


@r.post(
    "/verify",
    status_code=200,
    response_model=EmailVerifyReturn,
    responses={
        400: {"model": ErrorDetail},
    },
)
async def verify(
    payload: EmailVerifyPayload,
    db: Session = Depends(get_db),
):
    hash = payload.hash

    # TODO: write a cron-like to clean expired from UserSecret.

    # check if there is such verification in db. Also check expiration time.
    user_secret: Union[UserSecret, None] = (
        db.query(UserSecret)
        .filter(UserSecret.token == hash)
        .filter(
            func.age(func.now(), UserSecret.created_at)
            <= func.make_interval(0, 0, 0, 0, UserSecret.valid_for_hours),
        )
    ).first()
    if not user_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail("PASSWORD_INVALID"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user: Union[User, None] = (
        db.query(User).filter(User.id == user_secret.user_id).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail("USER_DOES_NOT_EXIST_V"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    euser = cast(User, user)

    if user and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail("USER_ALREADY_VERIFIED"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user and user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail("USER_INACTIVE_III"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    ### verify user
    user.is_verified = True  # type: ignore
    db.commit()

    ### delete user_secret
    db.delete(user_secret)
    db.commit()
    return {"detail": "verified"}


# ----------------------------------------------------


class PasswordResetRequestPayload(BaseModel):
    email: str


## In order to make it hard for malicious users to guess whether emails exist in
# our database, we always return 202 accepted.
@r.post(
    "/password_reset_request",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        424: {"model": ErrorDetail},
    },
)
async def password_reset_request(
    payload: PasswordResetRequestPayload,
    db=Depends(get_db),
):
    email = payload.email
    message = []
    do_send_mail: bool = True
    valid_email = get_normalized_email_or_406(email)
    if not valid_email:
        message.append("not valid mail")
        do_send_mail = False

    ## Check if there is such a user
    if do_send_mail:
        user: User = db.query(User).filter(User.email == email).first()
        if not user:
            message.append("not user")
            do_send_mail = False

    if do_send_mail and (not user.is_active):
        message.append("user is not active")
        do_send_mail = False

    ## eliminate attacks that make us send a lot of mail
    if do_send_mail:
        user_secret = get_valid_user_secret_by_user(db, user.id)
        if user_secret:
            do_send_mail = False
            message.append("user already has an active reset hash")

    if do_send_mail:
        message.append("Message sent")
        # TODO: by using JWT tokens like we do in login/get_active_user,
        # we could get away from using db here.
        # TODO 2: periodically delete old verification hashes from the db

        ## create a secret token and add to db
        secret_token = secrets.token_hex()
        user_secret = UserSecret(
            user_id=user.id,
            token=secret_token,
            is_reset=True,
            valid_for_hours=settings.PASSWORD_RESET_VALID_FOR_HOURS,
        )
        db.add(user_secret)
        db.commit()
        db.refresh(user_secret)

        send_mail_or_424(
            subject="Reset your password",
            html_content=html.password_reset_request(user.email, secret_token),
            sender_email=settings.MAIL_SENDER_EMAIL,
            sender_name=settings.MAIL_SENDER_NAME,
            to_email=user.email,
        )

    if settings.SAASR_DEBUG:
        return {"message": message}
    else:
        return {"detail": "Message sent"}


# -----------------------------


class PasswordResetPayload(BaseModel):
    password: str
    hash: str


@r.post(
    "/password_reset",
    status_code=200,
    responses={
        400: {"model": ErrorDetail},
    },
)
async def password_reset(
    payload: PasswordResetPayload,
    db: Session = Depends(get_db),
):
    password = payload.password
    hash = payload.hash

    password_is_valid = check_password_valid(password)

    raise_if(not password_is_valid, 400, "PASSWORD_INVALID_III")

    user_secret = get_valid_user_secret(db, hash)
    raise_if(not user_secret, 400, "HASH_DOES_NOT_EXIST_OR_EXPIRED_II")

    user: Union[User, None] = (
        db.query(User).filter(User.id == user_secret.user_id).first()
    )
    raise_if(not user, 400, "USER_DOES_NOT_EXIST_VI")
    raise_if(user and not user.is_active, 400, "USER_INACTIVE_IV")

    hashed_password = security.get_password_hash(password)
    user.hashed_password = hashed_password  # type: ignore
    db.commit()
    db.refresh(user)

    # TODO: why don't we delete here? try.
    # ### delete user_secret
    db.delete(user_secret)
    db.commit()
    return {"detail": "password reset"}
