from sqlalchemy import Column, Integer, Text, Date, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, index=True)
    email = Column(Text, unique=True, index=True)
    username = Column(Text, unique=True, index=True)
    password = Column(Text)

    comments = relationship("Comment", back_populates="user")
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
    pdf_url = Column(Text) 

    comments = relationship("Comment", back_populates="bill")
    
class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    bill_id = Column(Integer, ForeignKey("bills.id", ondelete="CASCADE"), index=True)
    comment = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="comments")
    bill = relationship("Bill", back_populates="comments")
    
    
class Poll(Base):
    __tablename__ = "polls"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, index=True)
    yes_votes = Column(Integer, default=0)
    no_votes = Column(Integer, default=0)
    
class UserPollVote(Base):
    __tablename__ = "user_poll_votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    poll_id = Column(Integer, ForeignKey('polls.id'))
    vote = Column(Boolean, nullable=False)  # "yes" or "no"

    user = relationship("User")
    poll = relationship("Poll")