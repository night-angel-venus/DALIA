from datetime import datetime, timedelta
from typing import Optional

# Packages for Auth
from jose import JWTError, jwt
from passlib.context import CryptContext

# FastAPI essentials
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# For getting env variables that were configured into settings
from app.config import settings

# Imports essential for Database Manipulation
from app.database import get_db
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import TokenData


# Password Encryption Block

# This variable is responsible for the reason
# why the password in the DB will look like
# $pbkdf2-sha256$100000$GoMwhpDyvleq1TqH0JqT0g$w3dDcbzKAzH3g1vgaV8o48imvvuMg/Ds9iGVFBbMedY

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
    pbkdf2_sha256__default_rounds=100000
)

# This simply tells where the auth endpoint is for Swagger UI 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/login")


# Actual Auth Functions


# ! Notice for the first 2 functions, pwd_context (The password config) is being used

# This simply checks if the plain password matches the hashed password
def verify_password(plain_password: str, hashed_password:str):
    return pwd_context.verify(plain_password, hashed_password)

# This hashes the password that is inputted
def get_password_hash(password:str):
    return pwd_context.hash(password)


# ! This is responsible for creating the Access Token that will be essential to 
# ! the whole Auth

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):

    # this takes in a copy of the data to be authorized
    to_encode = data.copy() 

    # this block chooses an expiration time for the token
    if expires_delta:
        expire = datetime.utcnow() + expires_delta

    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.TOKEN_EXPIRATION_MINUTES)

    to_encode.update({"exp":expire})


    # ! This is the actual creation of the JWT Token
    # it takes in the copied data, then env variables loaded into settings
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    
    return encoded_jwt


# FUNCTIONS TO GET CURRENT USER AND RESOLVE A SESSION TOKEN
# AND VERIFY IF THEY ARE IN A SESSION
# For most of the endpoints that require auth, this is how 
# the server will know which user is accessing which endpoint

async def get_current_user(
        token:str = Depends(oauth2_scheme), # ! its main parameter is the ACCESS TOKEN
        db: Session = Depends(get_db)
) -> User:



    # This block is for Error Handling
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail = "Unable to Validate Credentials",
        headers={"WWW-Authenticate":"Bearer"}
    )

    try:

        # The ENCODED jwt will be passed onto here and be DECODED to match a user
        # who logged in using their email and password

        payload = jwt.decode(token,settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Extracts the email
        email: str = payload.get("sub")
        # Error Handling
        if email is None:
            raise credentials_exception

        # right now this is unused
        token_data = TokenData(email=email)

    except JWTError:
        raise credentials_exception

    # Actual code that gets the USER from the DATABASE
    # Essentially a DB Query
    user = db.query(User).filter(User.email == email).first()
    
    if user is None:
        raise credentials_exception

    return user


# Currently unused blocks

async def get_admin(current:User = Depends(get_current_user)):
    if current.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin Privileges Required."
        )

    return current

async def get_user(current:User = Depends(get_current_user)):
    if current.role not in ["Admin", "User"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User or Admin Privileges Required!"
        )


