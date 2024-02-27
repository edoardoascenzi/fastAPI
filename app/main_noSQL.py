from fastapi import FastAPI
from fastapi import Response
from fastapi import status
from fastapi import HTTPException
from fastapi.params import Body
from typing import Optional
from pydantic import BaseModel
from random import randrange

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

app = FastAPI()

myPosts = [
    {"title":"Title 1", "content":"Content of post 1", "id":1},
    {"title":"Title 2", "content":"Content of post 2", "id":2},
]


@app.get("/posts")
def getPosts():
    return {'data': myPosts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def createPost(post: Post):
    # print(post.rating)
    # print(post.model_dump()) #method used to convert the post to dict
    postDict = post.model_dump()
    postDict["id"] = randrange(0,1000000)
    myPosts.append(postDict)
    return {'data':postDict}

@app.get("/posts/latest")
def latest():
    """
    bla bla
    """
    return {"data": myPosts[-1]}

@app.get("/posts/{id}") #path parameter
def getPost(id: int):
    post = list(filter(lambda postItem: postItem["id"] == id,myPosts)) #search for the specific post
    if len(post) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    return {"data": post[0]} 

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT) #204 when sth is deleted
def deletePost(id: int):
    post = list(filter(lambda postItem: postItem["id"] == id,myPosts)) #search for the specific post
    if len(post) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    myPosts.remove(post[0])
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def updatePost(id:int, post: Post): #with the PUT we need all the field
    postOld = list(filter(lambda postItem: postItem["id"] == id,myPosts)) #search for the specific post
    if len(postOld) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    myPosts.remove(postOld[0])
    postNew = post.model_dump()
    postNew["id"] = postOld[0]["id"]
    myPosts.append(postNew)
    return{"data": postNew}



