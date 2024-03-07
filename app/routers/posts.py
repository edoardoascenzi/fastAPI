from typing import List

from app import oauth2
from .. import models,schemas,utils
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import Depends, status, HTTPException, Response
from ..database import get_db
from fastapi import APIRouter
 
router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

@router.get("", response_model=List[schemas.ResponsePost])
def get_Posts(db: Session = Depends(get_db), currentUser = Depends(oauth2.getCurrentUser),
              limit: int = 10, skip: int = 0, search: str = ""):
    # posts = db.query(models.Post).all() #all the posts (like public social media)
    # posts = db.query(models.Post).filter(models.Post.user_id == currentUser.id).all() #this for specific only the logged in user posts
    # posts = db.query(models.Post).filter(models.Post.title.contains(search) | models.Post.content.contains(search)).limit(limit).offset(skip).all() #all the posts with filters
    # select posts.*, count(votes.post_id) as likes from posts left outer join votes on posts.id = votes.post_id group by posts.id;
    postsQuery = db.query(models.Post, func.count(models.Vote.post_id).label("likes")).join(models.Vote , models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id)
    posts = postsQuery.all()
    return posts

@router.post("", status_code=status.HTTP_201_CREATED , response_model=schemas.PostOut)
def create_Post(post: schemas.CreatePost, db: Session = Depends(get_db), currentUser = Depends(oauth2.getCurrentUser)):
    newPost = models.Post(user_id = currentUser.id, **post.model_dump())
    db.add(newPost) #add the new post to the db
    db.commit() #commit the db changes
    db.refresh(newPost) #retrive the newly created post and store it into newPost variable (the returning of the SQL query)
    return newPost

@router.get("/latest", response_model=schemas.ResponsePost)
def latest_post(db: Session = Depends(get_db), currentUser = Depends(oauth2.getCurrentUser)):
    # latestPost = cursor.execute(""" SELECT * FROM posts ORDER BY created_at DESC LIMIT 1;""").fetchone()
    # latestPost = db.query(models.Post).order_by(models.Post.created_at.desc()).limit(1).first()
    latestPost = db.query(models.Post, func.count(models.Vote.post_id).label("likes")).join(models.Vote , models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).order_by(models.Post.created_at.desc()).limit(1).first()
    return latestPost

@router.get("/{id}" , response_model=schemas.ResponsePost) #path parameter
def get_Post(id: int, db: Session = Depends(get_db), currentUser = Depends(oauth2.getCurrentUser)):
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    # joint with like
    post = db.query(models.Post, func.count(models.Vote.post_id).label("likes")).join(models.Vote , models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    # if post.user_id != currentUser.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT) #204 when sth is deleted
def delete_Post(id: int, db: Session = Depends(get_db), currentUser = Depends(oauth2.getCurrentUser)):
    postQuery = db.query(models.Post).filter(models.Post.id == id)
    post = postQuery.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    if post.user_id != currentUser.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    postQuery.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.PostOut)
def update_Post(id:int, post: schemas.UpdatePost , db: Session = Depends(get_db), currentUser = Depends(oauth2.getCurrentUser)): #with the PUT we need all the field
    updatePostQuery = db.query(models.Post).filter(models.Post.id == id)
    updatePost = updatePostQuery.first()
    if updatePost == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    if updatePost.user_id != currentUser.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    updatePostQuery.update(post.model_dump(),synchronize_session=False)
    db.commit()
    return updatePostQuery.first()

