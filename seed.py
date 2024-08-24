from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from app.auth import get_password_hash
from app import crud ,schemas

def seed_users(db: Session):
    user_data = [
        {"name": "John Doe", "email": "admin@gmail.com", "username": "john", "password": "password123"},
        {"name": "Jane Smith", "email": "jane@example.com", "username": "jane", "password": "password123"},
    ]

    for data in user_data:
        # Call the create_user method to handle user creation
        db_user = crud.create_user(db, schemas.UserCreate(**data))
def main():
    db = SessionLocal()
    seed_users(db)
    db.close()

if __name__ == "__main__":
    main()
