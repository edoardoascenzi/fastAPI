from datetime import datetime
from xmlrpc.client import ResponseError
from click import password_option
from pydantic import BaseModel, EmailStr, validator
from typing import Optional

from sqlalchemy import Integer

## USER

class UserBase(BaseModel):
    email: EmailStr
    password: str

class CreateUser(UserBase):
    pass

class ResponseUser(BaseModel):
    id: int
    email: str
    created_at: datetime

## AUTHENTICATION
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    accessToken: str
    tokenType: str

class TokenData(BaseModel):
    user_id: Optional[int] = None   

    
## POST

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class CreatePost(PostBase):
    pass

class UpdatePost(PostBase):
    published: bool

class ResponsePost(PostBase):
    published: bool
    created_at: datetime
    id: int
    user_id: int
    userOwner: ResponseUser

    # class Config:
    #     from_attributes = True

class ResponsePostLike(BaseModel):
    Post: ResponsePost
    likes: int

## VOTE
    
class Vote(BaseModel):
    post_id: int
    direction: int # 1 put vote, 0 remove vote

    @validator('direction')
    def checkDirection(cls, direction):
        if direction not in [0, 1]:
            raise ValueError('Direction must be either 0 or 1')
        return direction

class ResponseVote(BaseModel):
    post_id: int
    user_id: int
