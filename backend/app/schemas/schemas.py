from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from datetime import date, datetime
from app.enums import UserRoleEnum, ShiftTypeEnum

class CreateUser(BaseModel):
    username:str
    email: EmailStr
    password: str
    role: UserRoleEnum 

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRoleEnum

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

    class Config:
        from_attributes = True

    

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class CreateDTR(BaseModel):
    user_id: int
    shift_type: ShiftTypeEnum



class TimeInRequest(BaseModel):
    shift_type: ShiftTypeEnum


class DTRResponse(BaseModel):
    id: int
    date: date
    user_id: int
    shift_type: ShiftTypeEnum
    time_in: datetime 
    estimated_time_out: Optional[datetime] = None
    time_out: Optional[datetime] = None


    class Config:
        from_attributes = True
    