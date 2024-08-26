from sqlalchemy.orm import Session
from . import models, schemas,auth
import requests


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
        print(f"User with email {user.email} already exists.")
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

def get_bills(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Bill).offset(skip).limit(limit).all()

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