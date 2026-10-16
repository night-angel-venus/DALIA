# IMPORTS

# FASTAPI Essentials
from fastapi import FastAPI, HTTPException, APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm

# Database Essentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, DTR, SyncLogs
from app.schemas import CreateUser, UserResponse, Token, DTRResponse, TimeInRequest, SyncEvent
from app.enums import ShiftTypeEnum


# Auth Essentials
from app.auth.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)

# DTR Essentials
from app.services.dtr import user_time_in, user_time_out
from datetime import datetime, date

# RATE LIMITER Essentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# SECURITY HEADERS Essentials
from starlette.middleware.base import BaseHTTPMiddleware
import os


# Create the RATE LIMITER
# TEST_MODE is set to true only for the purpose of not making errors during testing
# Set to false once done testing
limiter = Limiter(key_func=get_remote_address, enabled=os.getenv("TEST_MODE") != "true")

# FASTAPI APP
app = FastAPI(title="DALIA", version="0.1.0")
router = APIRouter(prefix="/v1") # App Router

# Attach the rate limiter into app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# SECURITY HEADERS
class SecurityHeader(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response

app.add_middleware(SecurityHeader)


# API ENDPOINTS 

# For early development, just used to test if server is up and working
@router.get("/health", status_code=status.HTTP_200_OK)
def get_health():
    return {
        "status":"healthy",
        "current":"App is running" 
    }

# Register Endpoint
# For this project, this endpoint is here to use on Swagger UI and make adding users easier

@router.post("/register", response_model=UserResponse)
@limiter.limit("3/hour")
def register(request: Request, user: CreateUser, db: Session = Depends(get_db)):

    # Query an existing user from the DB
    existing_user = db.query(User).filter(User.email == user.email).first()

    # Error handler
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists."
        )

    # Create new user

    # Hash the user's password
    hashed_password = get_password_hash(user.password)

    # Create the new User Object
    new_user = User(
        username = user.username,
        email = user.email,
        password = hashed_password,
        role=user.role
    )

    # Stages the new user object in the session, to be added to the DB
    db.add(new_user)

    # commits the addition the new user to the DB
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db:Session = Depends(get_db)
):

    # Query an existing user
    # use the email from the form data to match with an email from the DB
    # it is called username because the auth uses that field name, but is actually email
    user = db.query(User).filter(User.email == form_data.username).first()

    # Error handler
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect Password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Create the Access Token
    access_token = create_access_token(
        data = {"sub": user.email, "role": user.role}
    )

    # Simply print to terminal
    print(f"User: {user.username}")
    print(f"Email: {user.email}")
    print(f"Token: {access_token}")


    return {
        "access_token": access_token,
        "token_type":"bearer",
        "user": user
        }


# Just a test endpoint to get the user currently logged in
@router.get("/me", response_model=UserResponse)
def me(current:User = Depends(get_current_user)):
    return current

# NOTE: if the time-in and time-out endpoints are not used and are replaced by the sync endpoint, remove these 2

# Time In Endpoint
@router.post("/dtr/time-in", response_model=DTRResponse, status_code=status.HTTP_201_CREATED)
def time_in(                                                                                                            
    payload:TimeInRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)):

    # Calling the function inside services/dtr.py and passing in the parameters
    # The API acts as the entry point for the data to be passed onto services/dtr.py
    # This was done to simplify the endpoint inside this main.py file
    dtr_time_in = user_time_in(
        db,
        current_user,
        payload.shift_type,
        datetime.now()
    )

    # Commit the Time in Data
    db.commit()
    db.refresh(dtr_time_in)

    return dtr_time_in

# Time out endpoint
# This is similar to time in, with the exception that 
# There is no Payload parameter
@router.post("/dtr/time-out", response_model=DTRResponse)
def time_out(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dtr_time_out = user_time_out(
        db,
        current_user,
        datetime.now()
    )

    db.commit()
    db.refresh(dtr_time_out)

    return dtr_time_out

# Get Today's DTR Endpoint
# Important for displaying what time the user has
# Timed in
@router.get("/dtr/today", response_model=DTRResponse | None)
def get_dtr_today(current_user:User=Depends(get_current_user), db:Session=Depends(get_db)):

    # Query to get the user's DTR for the day
    dtr_today = db.query(DTR).filter(
        DTR.user_id == current_user.id,
        DTR.date == date.today()
    ).first()

    
    return dtr_today

# Endpoint to get the DTR history of a user
# Right now, not implemented into main system flow
@router.get("/dtr/history", response_model=list[DTRResponse])
def get_dtr_all(
    current_user: User = Depends(get_current_user),
    db:Session = Depends(get_db)
):
    dtr_history = db.query(DTR).filter(
        DTR.user_id == current_user.id
    ).all()

    return dtr_history



# Sync Endpoint
# This endpoint is responsible for receiving the sqlite data 

@router.post("/dtr/sync")
@limiter.limit("60/minute")
def sync_dtr(
    request:Request,
    event: SyncEvent, # this contains data about the dtr
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Query an existing event_id in the Sync Logs
    existing_log = db.query(SyncLogs).filter(
        SyncLogs.user_event_id == event.user_event_id
    ).first()

    if existing_log:
        return {
            "status":"processed",
            "user_event_id": event.user_event_id
        }

    # Error Handler
    if event.user_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="Wrong user ID"
        )

    # Start of Sync Logic
    try:
        # Gets the timestamp of the payload (dtr)
        event_time = datetime.fromisoformat(event.payload["timestamp"])
    except (KeyError, ValueError):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="Invalid Timestamp"
        )

    # For time in events
    if event.event_type == "TIME_IN":
        try:
            shift = ShiftTypeEnum(event.payload["shift_type"])
        except (KeyError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Shift Type"
            )

        # Call the Time In function from services to add to DB
        dtr = user_time_in(db, current_user,shift, event_time)
    elif event.event_type == "TIME_OUT":
        dtr = user_time_out(db, current_user, event_time)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown event: {event.event_type}"
        )
    
    db.flush()

    # Create an object for Logs
    log = SyncLogs(
        user_event_id=event.user_event_id,
        dtr_id = dtr.id
    )


    # Add Log to DB
    db.add(log)
    db.commit()
    db.refresh(dtr)

    return {
        "status":"PROCESSED",
        "user_event_id":event.user_event_id
    }


app.include_router(router)