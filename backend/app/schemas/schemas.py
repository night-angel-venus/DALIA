from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from datetime import date, datetime

class UserRoleEnum(str, Enum):
    ADMIN = "Admin"
    USER = "User"

class ShiftTypeEnum(str, Enum):
    FULL_DAY = "Full Day (8 Hours)"
    HALF_DAY = "Half Day (4 Hours)"
    
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

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class CreateDTR(BaseModel):
    user_id: int
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
    