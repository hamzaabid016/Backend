from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status,Query, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from .. import schemas, crud
from ..auth import create_access_token, authenticate_user, get_current_user,oauth2_scheme,verify_password_reset_token,get_password_hash
from ..database import get_db
from .. import models, helpers,chatbot

ACCESS_TOKEN_EXPIRE_MINUTES = 1440

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
#, token: str = Depends(oauth2_scheme)
@router.get("/bills/", response_model=list[schemas.Bill])
def all_bills(db: Session = Depends(get_db)):
    bills = crud.get_bills(db)
    return bills

@router.get("/bills-bill/", response_model=list[schemas.Bills_bill])
def all_bills_bill(
    db: Session = Depends(get_db),
    limit: int = Query(40, le=100),  # Default limit is 15, max 100
    offset: int = Query(0, ge=0)    # Default offset is 0, must be non-negative
):
    # Fetch bills with limit and offset
    bills = db.query(models.BillsBill).offset(offset).limit(limit).all()
    
    if not bills:
        raise HTTPException(status_code=404, detail="No bills found")
    
    # Fetch related texts for each bill
    for bill in bills:
        bill.texts = db.query(models.BillsBillText).filter(models.BillsBillText.docid == bill.text_docid).all()
    
    return bills

@router.get("/bills-bill/{bill_id}", response_model=schemas.Bills_bill)
def get_single_bill(
    bill_id: int,  # The unique ID of the bill to fetch
    db: Session = Depends(get_db)
):
    # Fetch the bill by its ID
    bill = db.query(models.BillsBill).filter(models.BillsBill.id == bill_id).first()
    
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    # Fetch related texts for the bill
    bill.texts = db.query(models.BillsBillText).filter(models.BillsBillText.docid == bill.text_docid).all()
    
    return bill

@router.post("/seed-bills/")
def seed_bills_endpoint(db: Session = Depends(get_db)):
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
    bill = db.query(models.BillsBill).filter(models.BillsBill.id == comment.bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    # Create and add the comment
    db_comment = models.Comment(
        user_id=user.id,
        bill_id=comment.bill_id,
        comment=comment.comment
    )
    return crud.create_comment(db=db, comment=db_comment)

@router.get("/comments/{bill_id}", response_model=List[schemas.Comment])
def get_comments(bill_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Check if the bill exists
    bill = db.query(models.BillsBill).filter(models.BillsBill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    # Retrieve comments associated with the bill
    comments = bill.comments
    return comments

@router.delete("/comments/{comment_id}")
def delete_comments(comment_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Check if the bill exists
    user = get_current_user(token, db)
    if not user.is_moderator:
        raise HTTPException(status_code=403, detail="You do not have permission to delete a comment")

    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Retrieve comments associated with the bill
    db.delete(comment)
    db.commit()
    
    return {"message": "Comment deleted successfully"}

@router.post("/polls/{poll_id}/vote", response_model=schemas.UserPollVote)
def vote_poll(poll_id: int, vote: schemas.Vote, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Extract user from token
    user = get_current_user(token, db)
    
    # Register the user's vote
    db_vote = crud.vote_poll(db=db, user_id=user.id, poll_id=poll_id, vote=vote.vote)
    if db_vote is None:
         raise HTTPException(status_code=400, detail="User already voted with the same option")
    
    return db_vote

@router.get("/polls/", response_model=List[schemas.DetailPoll])
def get_poll(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_current_user(token, db)
    
    try:
        polls = crud.get_polls(db=db)
        
        # Fetch user's vote for each poll and add to the response
        for poll in polls:
            user_vote = db.query(models.UserPollVote).filter(
                models.UserPollVote.user_id == user.id,
                models.UserPollVote.poll_id == poll.id
            ).first()
            if user_vote:
                poll.current_user_vote = True if user_vote.vote else False
            else:
                poll.current_user_vote = None  # User has not voted

        return polls
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/polls/", response_model=schemas.Poll)
def create_poll(poll: schemas.PollCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_current_user(token, db)
    if not user.is_moderator:
        raise HTTPException(status_code=403, detail="You do not have permission to create a poll")

    try:
        return crud.create_poll(db=db, poll=poll)
    except SQLAlchemyError as e:
        db.rollback()  # Rollback the transaction in case of an error
        raise HTTPException(status_code=500, detail="An error occurred while creating the poll")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    
@router.get("/summarize/{bill_id}")
def summarize_bill(bill_id: int, db: Session = Depends(get_db)):
    # Fetch the bill from the database using the provided ID
    bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()  # Assuming Bill model exists
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    pdf_url = bill.pdf_url  # Assuming the Bill model has a 'pdf_url' field

    # Fetch and extract text from the PDF
    try:
        text = helpers.fetch_pdf_text(pdf_url)
        cleaned_text=helpers.clean_text(text)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"No decription available to summarize")

    # Generate a summary using OpenAI GPT
    summary = helpers.generate_summary(cleaned_text)

    return {"summary": summary}



@router.post("/chat/{bill_id}")
def chatbotfunc(
    bill_id: int,
    request: schemas.ChatRequest = Body(...),
    db: Session = Depends(get_db)
):
    try:
        # Fetch the bill from the database
        bill = db.query(models.BillsBill).filter(models.BillsBill.id == bill_id).first()
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")
        
        # Fetch the bill texts and summaries
        bill_texts = db.query(models.BillsBillText).filter(models.BillsBillText.docid == bill.text_docid).all()
        if bill_texts:
            summary = "\n".join([text.summary_en for text in bill_texts if text.summary_en])
        else:
            summary = "No summary available."
        
        # Prepare the bill information
        bill_info = {
            "bill_name": bill.name_en,
            "bill_number": bill.number,
            "summary": summary,
            "status": bill.status_code,
            "introduced_date": bill.introduced
        }
        
        # Extract conversation from the request body
        conversation = request.conversation if request.conversation else []
        
        # If no conversation history, start with a greeting
        if len(conversation) == 0:
            conversation.append({
                "role": "assistant",
                "content": f"The bill '{bill_info['bill_name']}' is being discussed. What would you like to know about it?"
            })
            return {"conversation": conversation}
        
        # Generate an updated conversation
        updated_conversation = chatbot.generate(conversation, bill_info)
        
        return {"conversation": updated_conversation}
    
    except HTTPException as http_err:
        # Handle HTTP exceptions
        raise http_err
    
    except Exception as ex:
        # Handle other exceptions
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/bills-bill/{bill_id}/vote")
def vote_on_bill(
    bill_id: int,
    upvote: bool,  
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)  # Extracting user token
    ):
    # Extract user from token
    user = get_current_user(token, db)
    
    # Retrieve the bill
    bill = db.query(models.BillsBill).filter(models.BillsBill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    # Check if the user has already voted on this bill
    existing_vote = db.query(models.UserBillVote).filter(
        models.UserBillVote.user_id == user.id,
        models.UserBillVote.bill_id == bill_id
    ).first()

    if existing_vote:
        # If user has already voted
        if existing_vote.upvote == upvote:
            # No change in vote, do nothing
            return {"detail": "No change in vote", "vote": existing_vote}
        else:
            # Change in vote, update counts
            if existing_vote.upvote:
                # Previous vote was upvote
                bill.upvotes -= 1
            else:
                # Previous vote was downvote
                bill.downvotes -= 1

            if upvote:
                # New vote is upvote
                bill.upvotes += 1
            else:
                # New vote is downvote
                bill.downvotes += 1

            existing_vote.upvote = upvote
    else:
        # New vote
        if upvote:
            bill.upvotes += 1
        else:
            bill.downvotes += 1
        
        # Create new vote record
        db_vote = models.UserBillVote(user_id=user.id, bill_id=bill_id, upvote=upvote)
        db.add(db_vote)
    
    db.commit()
    db.refresh(bill)
    
    # Refresh the existing_vote if it was updated
    if existing_vote:
        db.refresh(existing_vote)
    
    
    return {"detail": "Vote recorded", "vote": existing_vote if existing_vote else db_vote}