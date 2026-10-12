from fastapi import FastAPI, HTTPException, status, APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, DTR
from app.schemas import CreateUser, UserResponse, Token, DTRResponse, TimeInRequest
from app.auth.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)

from app.services.dtr import user_time_in, user_time_out

from datetime import datetime, date


app = FastAPI(title="DALIA", version="0.1.0")

router = APIRouter(prefix="/v1")


@router.get("/health", status_code=status.HTTP_200_OK)
def get_health():
    return {
        "status":"healthy",
        "current":"App is running" 
    }

@router.post("/register", response_model=UserResponse)
def register(request: Request, user: CreateUser, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists."
        )

    # create new user

    hashed_password = get_password_hash(user.password)

    new_user = User(
        username = user.username,
        email = user.email,
        password = hashed_password,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db:Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()

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

    print(f"User: {user.username}")
    print(f"Email: {user.email}")
    print(f"Token: {access_token}")


    return {
        "access_token": access_token,
        "token_type":"bearer",
        "user": user
        }


@router.get("/me", response_model=UserResponse)
def me(current:User = Depends(get_current_user)):
    return current

# ENDPOINT FOR TIME IN DTR


@router.post("/dtr/time-in", response_model=DTRResponse, status_code=status.HTTP_201_CREATED)
def time_in(
    payload:TimeInRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)):

    dtr_time_in = user_time_in(
        db,
        current_user,
        payload.shift_type,
        datetime.now()
    )
    db.commit()
    db.refresh(dtr_time_in)

    return dtr_time_in

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


@router.get("/dtr/today", response_model=DTRResponse)
def get_dtr_today(current_user:User=Depends(get_current_user), db:Session=Depends(get_db)):

    dtr_today = db.query(DTR).filter(
        DTR.user_id == current_user.id,
        DTR.date == date.today()
    ).first()

    if dtr_today is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DTR not found"
        )

    return dtr_today

@router.get("/dtr/history", response_model=list[DTRResponse])
def get_dtr_all(
    current_user: User = Depends(get_current_user),
    db:Session = Depends(get_db)
):
    dtr_history = db.query(DTR).filter(
        DTR.user_id == current_user.id
    ).all()

    if dtr_history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DTR History not found"
        )

    return dtr_history



app.include_router(router)