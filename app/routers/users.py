from typing import List
from .. import models,schemas,utils
from fastapi import HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi import status
from ..database import get_db
from fastapi import APIRouter

router = APIRouter(
    prefix="/users", 
    tags=['Users']
)

@router.get("", response_model=List[schemas.ResponseUser])
def get_Users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@router.post("", status_code=status.HTTP_201_CREATED , response_model=schemas.ResponseUser)
def create_User(user: schemas.CreateUser, db: Session = Depends(get_db)):
    
    user.password = utils.hash(user.password)
    newUser = models.User(**user.model_dump())
    db.add(newUser) 
    db.commit()
    db.refresh(newUser)
    return newUser

@router.get("/{id}" , response_model=schemas.ResponseUser)
def get_User(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} does not exist")
    return user