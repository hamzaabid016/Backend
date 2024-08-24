from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..auth import create_access_token, authenticate_user, get_current_user,oauth2_scheme
from ..database import get_db


ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()
@router.post("/login", response_model=schemas.Token)
def login(form_data: schemas.LoginForm , db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.email, form_data.password)
    if not user: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=schemas.User)
def read_users_me(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(token, db)
    return current_user

@router.post("/register/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@router.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users



@router.get("/bills/", response_model=list[schemas.Bill])
def read_bills(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    bills = crud.get_bills(db, skip=skip, limit=limit)
    return bills

@router.post("/seed-bills/")
def seed_bills_endpoint(db: Session = Depends(get_db)):
    crud.seed_bills(db)
    return {"message": "Bills data seeded successfully"}