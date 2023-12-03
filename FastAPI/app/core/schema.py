from pydantic import BaseModel, EmailStr
from typing import List
from enum import Enum


class EmailSchema(BaseModel):
    email: List[EmailStr]

class ErrorDetail(BaseModel):
    is_error_detail:bool =True
    error_code: str
    error_english: str

    class Config:
        orm_mode = True   


# class ErrorCode(ErrorDetail, Enum):
#     TEAM_NAME_IS_EMPTY = ErrorDetail(error_code='TEAM_NAME_IS_EMPTY',error_english="Teaam name is empty")




