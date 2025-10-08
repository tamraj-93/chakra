from pydantic import BaseModel
from typing import Optional, List

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True  # Updated name for 'orm_mode' in Pydantic v2

class Token(BaseModel):
    access_token: str
    token_type: str
        
class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: User