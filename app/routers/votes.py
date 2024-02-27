from typing import List

from app import oauth2
from .. import models,schemas,utils
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException, Response
from ..database import get_db
from fastapi import APIRouter
 

router = APIRouter(
    prefix="/vote", 
    tags=['Vote']
)

@router.get("", response_model=List[schemas.ResponseVote])
def get_Votes(db: Session = Depends(get_db), currentUser = Depends(oauth2.getCurrentUser)):
    votes = db.query(models.Vote).all() #all the posts (like public social media)
    
    return votes

@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.ResponseVote)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), currentUser = Depends(oauth2.getCurrentUser)):

    postQuery = db.query(models.Post).filter(models.Post.id == vote.post_id)
    if postQuery.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {vote.post_id} does not exist")
    
    voteQuery = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id , models.Vote.user_id == currentUser.id)
    foundVote = voteQuery.first()

    if vote.direction == 1:
        if foundVote != None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User {currentUser.id} already like post {vote.post_id}")
        newVote = models.Vote(post_id = vote.post_id, user_id = currentUser.id)
        db.add(newVote)
        db.commit()
        # db.refresh(newVote)
        return newVote
    
    else:
        if foundVote == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {currentUser.id} does not like post {vote.post_id}")
        voteQuery.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
