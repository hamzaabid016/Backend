from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..auth import create_access_token, authenticate_user, get_current_user,oauth2_scheme,verify_password_reset_token,get_password_hash
from ..database import get_db
from .. import models

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
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/bills/{bill_id}", response_model=schemas.Bill)
def bill(bill_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    if not bill_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Please send bill id")
    bill = crud.get_bill_by_id(db, bill_id=bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@router.get("/bills/", response_model=list[schemas.Bill])
def all_bills(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    bills = crud.get_bills(db, skip=skip, limit=limit)
    return bills

@router.post("/seed-bills/")
def seed_bills_endpoint(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    crud.seed_bills(db)
    return {"message": "Bills data seeded successfully"}


@router.post("/forgot_password/")
def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate a reset token (expires in 15 minutes)
    reset_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=15))

    """ 
    Here i need to typically send an email to the user with the reset token
    but i am not doind that right now will do in future
    """
    print(f"Reset token for {email}: {reset_token}")  # This is just for demonstration purposes

    return {"message": "Password reset email sent","reset_token":reset_token}


@router.post("/reset_password/")
def reset_password(request: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    email = verify_password_reset_token(request.token)
    if email is None:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the user's password
    hashed_password = get_password_hash(request.new_password)
    user.password = hashed_password
    db.commit()

    return {"message": "Password reset successfully"}


@router.post("/comments/", response_model=schemas.CommentCreate)
def add_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Check if the user exists
    user = get_current_user(token,db)
    user = db.query(models.User).filter(models.User.id == user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the bill exists
    bill = db.query(models.Bill).filter(models.Bill.id == comment.bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    # Create and add the comment
    db_comment = models.Comment(
        user_id=user.id,
        bill_id=comment.bill_id,
        comment=comment.comment
    )
    return crud.create_comment(db=db, comment=db_comment)