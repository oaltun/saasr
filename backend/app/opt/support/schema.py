from pydantic import BaseModel
from datetime import datetime
from typing import List
import uuid

from app.user.schema import UserOut, UserOutMailNames

### Message Endpoint ###
class MessageBase(BaseModel):
    issue_id: uuid.UUID
    text: str


class MessageCreate(MessageBase):
    pass


class MessageOut(MessageBase):
    id: uuid.UUID
    created_at: datetime
    #owner_id: uuid.UUID
    owner: UserOutMailNames

    class Config:
        orm_mode = True


### Issue Endpoint ###
class IssueBase(BaseModel):
    title: str


class IssueCreate(IssueBase):
    message_text: str


class IssueOutInList(IssueBase):
    id: uuid.UUID
    #owner_id: uuid.UUID
    owner: UserOutMailNames
    created_at: datetime
    is_closed: bool
    closed_at: datetime = None
    #closer_id: uuid.UUID = None
    closer: UserOutMailNames = None

    class Config:
        orm_mode = True


class IssueOut(IssueOutInList):
    messages: List[MessageOut] = []
    pass


class IssueStatusUpdate(BaseModel):
    is_closed: bool
