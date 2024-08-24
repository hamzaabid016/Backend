from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models

def seed_users(db: Session):
    user_data = [
        {"name": "John Doe", "email": "john@example.com", "username": "john", "password": "password123"},
        {"name": "Jane Smith", "email": "jane@example.com", "username": "jane", "password": "password123"},
    ]

    for data in user_data:
        db_user = models.User(**data)
        db.add(db_user)
    db.commit()

def main():
    db = SessionLocal()
    seed_users(db)
    db.close()

if __name__ == "__main__":
    main()
