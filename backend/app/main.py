from fastapi import FastAPI, HTTPException, status, APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import CreateUser, UserResponse, Token
from app.auth.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)


app = FastAPI(title="DALIA", version="0.1.0")


@app.get("/health", status_code=status.HTTP_200_OK)
def get_health():
    return {
        "status":"healthy",
        "current":"App is running" 
    }

@app.post("/register", response_model=UserResponse)
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

@app.post("/login", response_model=Token)
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


@app.get("/me", response_model=UserResponse)
def me(current:User = Depends(get_current_user)):
    return current