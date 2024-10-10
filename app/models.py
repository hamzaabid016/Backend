from sqlalchemy import Column, Integer, Text, Date, Boolean, ForeignKey, TIMESTAMP,String,DateTime,UniqueConstraint
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
    is_moderator = Column(Boolean, default=False)
    profile_picture = Column(Text, nullable=True)
    
    comments = relationship("Comment", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # Link to the user
    message = Column(Text)
    read = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="notifications")
    
    
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
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    
class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    bill_id = Column(Integer, ForeignKey("bills_bill.id", ondelete="CASCADE"), index=True)
    comment = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="comments")
    bill = relationship("BillsBill", back_populates="comments")
    
    
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
    ipaddress = Column(Text, nullable=True)  # New field for IP address
    location = Column(Text, nullable=True)
    user = relationship("User")
    poll = relationship("Poll")
    
    
    
    
class BillsBill(Base):
    __tablename__ = 'bills_bill'

    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(Text, nullable=False) 
    number = Column(String(10), nullable=True) 
    number_only = Column(Integer, nullable=True) 
    sponsor_member_id = Column(Integer, nullable=True) 
    privatemember = Column(Boolean, nullable=True) 
    sponsor_politician_id = Column(Integer, nullable=True) 
    law = Column(Boolean, nullable=True) 
    added = Column(Date, nullable=True)  
    upvotes = Column(Integer, default=0, nullable=False) 
    downvotes = Column(Integer, default=0, nullable=False) 
    institution = Column(String(1), nullable=True) 
    name_fr = Column(Text, nullable=True) 
    short_title_en = Column(Text, nullable=True) 
    short_title_fr = Column(Text, nullable=True) 
    status_date = Column(Date, nullable=True) 
    introduced = Column(Date, nullable=True) 
    text_docid = Column(Integer, nullable=True,unique=True)  
    status_code = Column(String(50), nullable=False)  

    # Relationships
    texts = relationship("BillsBillText", back_populates="bill")
    comments = relationship("Comment", back_populates="bill")

class BillsBillText(Base):
    __tablename__ = 'bills_billtext'

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey('bills_bill.id', deferrable=True, initially='DEFERRED'), nullable=False)
    docid = Column(Integer, nullable=False)
    created = Column(Text, nullable=False)
    text_en = Column(Text, nullable=False)
    text_fr = Column(Text, nullable=True)
    summary_en = Column(Text, nullable=True)

    # Relationship back to bills_bill
    bill = relationship("BillsBill", back_populates="texts")


class CoreParty(Base):
    __tablename__ = "core_party"

    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String(100), nullable=False)
    slug = Column(String(10), nullable=False)
    short_name_en = Column(String(100), nullable=False)
    name_fr = Column(String(100), nullable=False)
    short_name_fr = Column(String(100), nullable=False)

class CorePolitician(Base):
    __tablename__ = "core_politician"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    name_given = Column(String(50), nullable=False)
    name_family = Column(String(50), nullable=False)
    dob = Column(Date)
    gender = Column(String(1), nullable=False)
    headshot = Column(String(100))
    slug = Column(String(30), nullable=False)
    headshot_thumbnail = Column(String(100))
    

    # Relationship to core_politicianinfo (one politician can have many info entries)
    politician_info = relationship("CorePoliticianInfo", back_populates="politician")


class CorePoliticianInfo(Base):
    __tablename__ = "core_politicianinfo"

    id = Column(Integer, primary_key=True, index=True)
    politician_id = Column(Integer, ForeignKey('core_politician.id', ondelete="CASCADE"), nullable=False)
    value = Column(Text, nullable=False)
    schema = Column(String(40), nullable=False)
    created = Column(DateTime)

    # Relationship to core_politician
    politician = relationship("CorePolitician", back_populates="politician_info")
    
    
    
class UserBillVote(Base):
    __tablename__ = "user_bill_votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    bill_id = Column(Integer, ForeignKey('bills_bill.id'))
    upvote = Column(Boolean, nullable=True)  # True for upvote, False for downvote
    
    user = relationship("User")
    bill = relationship("BillsBill")

    __table_args__ = (
        UniqueConstraint('user_id', 'bill_id', name='unique_user_bill_vote'),
    )