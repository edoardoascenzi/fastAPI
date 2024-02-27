from tkinter import CASCADE
from annotated_types import Timezone
from .database import Base
from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, null, text
from sqlalchemy.orm import relationship

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False) 
    published = Column(Boolean, nullable=False , server_default='true')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    # created_by = Column(String, server_default='true')
    user_id = Column(Integer, ForeignKey("users.id", ondelete=CASCADE), nullable=False)

    userOwner = relationship("User") #this is referenced to the User Class and automatically fetch all the information he find about that user

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))

class Vote(Base):
    __tablename__ = 'votes'
    post_id = Column(Integer, ForeignKey("posts.id", ondelete=CASCADE), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete=CASCADE), primary_key=True, nullable=False)
