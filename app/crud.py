from sqlalchemy.orm import Session
from . import models, schemas,auth,helpers
import requests
from fastapi import HTTPException 

def get_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        return existing_user 
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        username=user.username,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_bill(db: Session, bill_id: int):
    return db.query(models.Bill).filter(models.Bill.id == bill_id).first()

def get_bill_by_id(db: Session, bill_id: int):
    return db.query(models.Bill).filter(models.Bill.id == bill_id).first()

def get_bills(db: Session):
    return db.query(models.Bill).all()

EXTERNAL_API_URL = "https://api.openparliament.ca/bills/"

def fetch_bills_from_external_api(url: str):
    headers = {
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def seed_bills(db: Session, initial_url: str = EXTERNAL_API_URL):  
    url = initial_url
    while url:
        data = fetch_bills_from_external_api(url)
        if not data:
            break

        # Process each bill from the current page
        for item in data.get('objects', []):
            bill_data = {
                "session": item.get("session"),
                "introduced": item.get("introduced"),
                "name": item.get("name", {}).get("en", ""),
                "number": item.get("number"),
                "home_chamber": "",  # Placeholder
                "law": False,  # Placeholder
                "sponsor_politician_url": "",  # Placeholder
                "sponsor_politician_membership_url": "",  # Placeholder
                "status": "",  # Placeholder
            }

            # Create or update the bill in the database
            db_bill = models.Bill(**bill_data)
            db_bill.pdf_url= helpers.convert_to_pdf_url(item.get('url', ''))
            
            db.add(db_bill)

            # Fetch additional details from the URL if necessary
            bill_details = fetch_bills_from_external_api(f"https://api.openparliament.ca{item.get('url', '')}")
            if bill_details:
                db_bill.status = bill_details.get("status", {}).get("en", db_bill.status)
        
        
        db.commit()

        # Get the next page URL
        next_url = data.get('pagination', {}).get('next_url')
        if next_url:
            url = f"https://api.openparliament.ca{next_url}"
        else:
            url = None
            
            
def create_comment(db: Session, comment: models.Comment):
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def vote_poll(db: Session, user_id: int, poll_id: int, vote: bool ,ipaddress: str, location: str):
    # Check if the user has already voted
    existing_vote = db.query(models.UserPollVote).filter(
        models.UserPollVote.user_id == user_id,
        models.UserPollVote.poll_id == poll_id
    ).first()
    
  
    ip_vote = db.query(models.UserPollVote).filter(
        models.UserPollVote.ipaddress == ipaddress,
        models.UserPollVote.poll_id == poll_id
    ).first()
    
    
    poll = db.query(models.Poll).filter(models.Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    if ip_vote:
        raise HTTPException(status_code=400, detail="A vote from this IP address has already been cast for this poll.")


    if existing_vote:
        if existing_vote.vote == vote:
            return None  
        else:
            # If the vote is different, update it
            if  vote:
                poll.yes_votes +=1
                poll.no_votes -=1
            else:
                poll.no_votes +=1
                poll.yes_votes -=1
            existing_vote.vote = vote
            existing_vote.ipaddress = ipaddress  # Save IP address
            existing_vote.location = location
    else:
        # Add new vote
        if vote:
            poll.yes_votes +=1
        else:
            poll.no_votes +=1
        db_vote = models.UserPollVote(user_id=user_id, poll_id=poll_id, vote=vote,ipaddress=ipaddress, location=location)
        db.add(db_vote)

    db.commit()
    db.refresh(poll) 
    db.refresh(existing_vote if existing_vote else db_vote)
    return existing_vote if existing_vote else db_vote

def get_polls(db: Session):
    return db.query(models.Poll).all()

def create_poll(db: Session, poll: schemas.PollCreate):
    db_poll = models.Poll(question=poll.question)
    db.add(db_poll)
    db.commit()
    db.refresh(db_poll)
    return db_poll