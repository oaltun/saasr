import uuid
from app.core.error import error_detail
from fastapi import  status, HTTPException
from sqlalchemy.orm import Session
import typing as t

from . import model, schema
from app.core.security import get_password_hash
from email_validator import validate_email, EmailNotValidError # type: ignore
import secrets
from typing import Union, cast


from app.user.model import User, UserSecret
from app.core.error import error_detail
from fastapi import (
    status,
    HTTPException
)


from sqlalchemy.orm import Session
from sqlalchemy import func


from app.config import settings
from password_validator import PasswordValidator # type: ignore
from app.core.mail import send_mail_or_424
from app.user import html


def get_normalized_email_or_406(email: str):
    try:
        # Validate & take the normalized form of the email
        # address for all logic beyond this point (especially
        # before going to a database query where equality
        # does not take into account normalization).
        email = validate_email(email).email
    except EmailNotValidError as e:
        print("(1e39)")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("EMAIL_INVALID")
        )
    return email


def get_user_or_404(db: Session, user_id: uuid.UUID)-> model.User:
    user = db.query(model.User).filter(model.User.id == user_id).first()
    if not user:
        print("e393")
        raise HTTPException(
            status_code=404, 
            detail=error_detail("USER_DOES_NOT_EXIST_II")
        )
    return user


def get_user_by_email(db: Session, email: str) -> Union[model.User,None]:
    return db.query(model.User).filter(model.User.email == email).first()


def get_users(
    db: Session, skip: int = 0, limit: int = 100
) -> t.List[model.User]:
    return db.query(model.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schema.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = model.User(
        name=user.name,
        surname=user.surname,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def delete_user_or_404(db: Session, user_id: uuid.UUID):
    user = get_user_or_404(db, user_id)
    if not user:
        print("(393f)")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=error_detail("USER_DOES_NOT_EXIST_III"))
    db.delete(user)
    db.commit()
    return user


def edit_user_or_404(
    db: Session, user_id: uuid.UUID, user: schema.UserEdit
) -> schema.User:
    db_user = get_user_or_404(db, user_id)
    if not db_user:
        print("(fdeb)")
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, 
            detail=error_detail("USER_DOES_NOT_EXIST_IV")
        )
    update_data = user.dict(exclude_unset=True)

    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(user.password)
        del update_data["password"]

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user






def send_email_verification_or_424(payload, db):
    print("send_email_verification. Email is "+payload.email)
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

    if do_send_mail and user.is_verified:
        message.append("user is verified")
        do_send_mail = False

    if do_send_mail and user.is_superuser:
        message.append("user is superuser")
        do_send_mail = False

    if do_send_mail and (not user.is_active):
        message.append("user is not active")
        do_send_mail = False

    if do_send_mail:
        message.append("Message sent")
        ## create a secret token and add to db
        # TODO: by using JWT tokens like we do in login/get_active_user,
        # we could get away from using db here.
        # TODO 2: periodically delete old verification hashes from the db
        secret_token = secrets.token_urlsafe()
        user_secret = UserSecret(
            user_id=user.id,
            token=secret_token,
            is_verification=True,
            valid_for_hours=settings.EMAIL_VERIFICATION_VALID_FOR_HOURS,
        )
        db.add(user_secret)
        db.commit()
        db.refresh(user_secret)

        # TODO: send email using background_tasks or a task queue like celery.
        send_mail_or_424(
            subject="Activate your account", 
            html_content=html.verify_request(user.email, secret_token),
            sender_email=settings.MAIL_SENDER_EMAIL,
            sender_name=settings.MAIL_SENDER_NAME, 
            to_email=user.email,
        )
        
    return message




def check_password_valid(password):
    schema = PasswordValidator()
    # fmt: off
    schema.min(8).max(100).has().uppercase().has().lowercase().has().digits().has().symbols().has().no().spaces()
    # fmt: on

    return schema.validate(password)


def is_valid_username(username: str):
    if len(username) < 2:
        return False
    for i in range(len(username)):
        if not (
            (ord(username[i]) >= 97 and ord(username[i]) <= 122)
            or (ord(username[i]) >= 48 and ord(username[i]) <= 57)
        ):
            return False

    return True

def get_valid_user_secret_by_user(db, user_id):
    # TODO: write a cron-like to clean expired from UserSecret.

    # check if there is such hash in db. Also check expiration time.
    q = (
        db.query(UserSecret)
        .filter(UserSecret.user_id == user_id)
        .filter(UserSecret.is_reset==True)
        .filter(
            func.age(func.now(), UserSecret.created_at)
            <= func.make_interval(0, 0, 0, 0, UserSecret.valid_for_hours),
        )
    )
    return cast(Union[UserSecret,None],q.first())  
    # return q.first()



def get_valid_user_secret(db, hash):
    # TODO: write a cron-like to clean expired from UserSecret.

    # check if there is such hash in db. Also check expiration time.
    q = (
        db.query(UserSecret)
        .filter(UserSecret.token == hash)
        .filter(
            func.age(func.now(), UserSecret.created_at)
            <= func.make_interval(0, 0, 0, 0, UserSecret.valid_for_hours),
        )
    )

    return cast(Union[UserSecret,None],q.first())  

