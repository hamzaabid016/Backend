from pydantic import BaseModel
from typing import Optional, Dict
from datetime import date
class UserBase(BaseModel):
    name: str
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class BillBase(BaseModel):
    session: str
    introduced: date
    name: str
    number: str
    home_chamber: str
    law: bool
    sponsor_politician_url: str
    sponsor_politician_membership_url: str
    status: str
    
class BillCreate(BillBase):
    pass

class Bill(BillBase):
    id: int

    class Config:
        orm_mode = True