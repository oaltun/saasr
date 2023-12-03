from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr
import typing as t


class EmailSchema(BaseModel):
    email: t.List[EmailStr]


class UserOutMailNames(BaseModel):
    id: uuid.UUID
    email: str
    name: t.Union[str,None] = None
    surname: t.Union[str,None] = None

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str
    is_verified:bool=False
    is_superuser: bool = False
    is_active: bool = True
    name: t.Union[str,None] = None
    surname: t.Union[str,None] = None


class UserOut(UserBase):
    class Config:
        orm_mode = True

class UserOutFull(UserOut):
    id: uuid.UUID
    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str

    class Config:
        orm_mode = True


class UserEdit(UserBase):
    password: t.Optional[str] = None

    class Config:
        orm_mode = True


class User(UserBase):
    id: uuid.UUID

    class Config:
        orm_mode = True


class UserSubscriptionInfo(BaseModel):
    invitation_count: int
    participation_count: int
    term_end: datetime

    class Config:
        orm_mode = True


class AccessToken(BaseModel):
    access_token: str
    token_type: t.Literal['bearer', ]


class Permissions(BaseModel):
    prm: t.Literal["admin","user"]



class TokenRequired(Permissions):
    sub: EmailStr

class TokenOutRequired(TokenRequired):
    exp: datetime

class TokenOutData(TokenOutRequired):
    uid: str
    td: int
    ia: t.Literal[1,0]
    isu: t.Literal[1,0]
    iv: t.Literal[1,0]
    pc: t.Union[int,None]
    ic: t.Union[int,None]
