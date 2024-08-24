from sqlalchemy import Column, Integer, Text, Date, Boolean
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, index=True)
    email = Column(Text, unique=True, index=True)
    username = Column(Text, unique=True, index=True)
    password = Column(Text)

class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    session = Column(Text, index=True)
    introduced = Column(Date)
    name = Column(Text)
    number = Column(Text)
    home_chamber = Column(Text)
    law = Column(Boolean)
    sponsor_politician_url = Column(Text)
    sponsor_politician_membership_url = Column(Text)
    status = Column(Text)
