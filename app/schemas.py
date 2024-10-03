from pydantic import BaseModel
from typing import Optional, Dict,List
from datetime import date,datetime

class LoginForm(BaseModel):
    email: str
    password: str
class UserBase(BaseModel):
    name: str
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_moderator: bool = False
    profile_picture:str
    

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user:User

class TokenData(BaseModel):
    email: str

class BillBase(BaseModel):
    session: str
    introduced: Optional[date]
    name: str
    number: str
    home_chamber: str
    law: bool
    sponsor_politician_url: str
    sponsor_politician_membership_url: str
    status: str
    pdf_url:str
    
class BillCreate(BillBase):
    pass

class Bill(BillBase):
    id: int

    class Config:
        orm_mode = True
        
class ForgotPasswordRequest(BaseModel):
    email: str
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str
    
class CommentCreate(BaseModel):
    bill_id: int
    comment: str
class Comment(BaseModel):
    id: int
    user_id: int
    bill_id: int
    comment: str
    created_at: datetime

    class Config:
        orm_mode = True
        
        
        
class Vote(BaseModel):
    vote: bool 

class UserPollVoteBase(BaseModel):
    user_id: int
    poll_id: int
    vote: bool 

class UserPollVote(UserPollVoteBase):
    id: int

    class Config:
        orm_mode = True
        
        
class PollCreate(BaseModel):
    question: str
class Poll(BaseModel):
    id : int
    question: str
    yes_votes: int
    no_votes: int

class DetailPoll(Poll):
    current_user_vote: Optional[bool] = None  # This field will be dynamically populated

    class Config:
        orm_mode = True
        
class BillsBillText(BaseModel):
    id: int
    bill_id: int
    docid: int
    created: datetime
    text_en: str
    # text_fr: str
    summary_en: Optional[str]

    class Config:
        orm_mode = True   
        
        
class Bills_bill(BaseModel):
    id: int
    name_en: str
    number: str
    number_only: int
    sponsor_member_id: Optional[int]
    privatemember: Optional[bool]
    sponsor_politician_id: Optional[int]
    law: Optional[bool]
    added: date
    upvotes: int
    downvotes: int
    institution: str
    #name_fr: str
    short_title_en: str
    #short_title_fr: str
    status_date: Optional[date]
    introduced: Optional[date]
    text_docid: Optional[int]
    status_code: str
    texts: Optional[List[BillsBillText]]

    class Config:
        orm_mode = True
        
        
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    conversation: Optional[List[Message]] = None 
    
    
class Notification(BaseModel):
    id: int
    user_id: int
    message: str
    read: bool
    class Config:
        orm_mode = True