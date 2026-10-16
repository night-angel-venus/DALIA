from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from app.enums import UserRoleEnum, ShiftTypeEnum

# SCHEMAS
# These essentially define the different forms that the data can take.
# Each Schema declares which bits of data they accept or will return

class CreateUser(BaseModel):
    
    #This schema only accepts the following in order to create a user: 
    username:str
    email: EmailStr
    password: str
    role: UserRoleEnum 

class UserResponse(BaseModel):

    # Once a user is being returned/queried, This schema will only return:

    id: int
    username: str
    email: EmailStr
    role: UserRoleEnum

    class Config:
        from_attributes = True

class Token(BaseModel):

    # This schema is important as it returns information
    # about who is logged in and their token itself
    # This is useful for testing in Thunder Client/Postman

    access_token: str
    token_type: str
    user: UserResponse

    class Config:
        from_attributes = True


class TokenData(BaseModel):

    # this might be unused
    email: Optional[str] = None
    role: Optional[str] = None

class CreateDTR(BaseModel):

    # Creating a DTR only needs these 2:
    user_id: int
    shift_type: ShiftTypeEnum

class TimeInRequest(BaseModel):

    # Timing in only needs:
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

class SyncEvent(BaseModel):
    user_event_id:str
    user_id: int
    event_type: str
    payload: dict
    created_at: datetime
    