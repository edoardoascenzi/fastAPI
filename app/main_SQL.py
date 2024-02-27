from fastapi import FastAPI
from fastapi import Response
from fastapi import status
from fastapi import HTTPException
from fastapi.params import Body
from typing import Optional
from pydantic import BaseModel
from random import randrange
import time
import psycopg


class Post(BaseModel):
    title: str
    content: str
    published: Optional[bool] = True
    # rating: Optional[int] = None

# postKeysList = list(Post.model_json_schema()['properties'].keys())

while True:
    try:
        conn = psycopg.connect(host='localhost',dbname='fastapi',user='postgres',password='Pollettino',row_factory=psycopg.rows.dict_row)
        cursor = conn.cursor()
        print("Database connected successfully!")
        break
    except Exception as error:
        print("Connection Failed!\nError: ", error)
        time.sleep(10)

app = FastAPI()

myPosts = [
    {"title":"Title 1", "content":"Content of post 1", "id":1},
    {"title":"Title 2", "content":"Content of post 2", "id":2},
]


@app.get("/posts")
def getPosts():
    posts = cursor.execute("""SELECT * FROM posts;""").fetchall()
    return {'data': posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def createPost(post: Post):

    newPost = cursor.execute(""" INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING *; """,
                   (post.title,post.content,post.published)).fetchone()
    conn.commit()
    return {'data': newPost}

@app.get("/posts/latest")
def latest():
    latestPost = cursor.execute(""" SELECT * FROM posts ORDER BY created_at DESC LIMIT 1;""").fetchone()
    return {"data": latestPost}

@app.get("/posts/{id}") #path parameter
def getPost(id: int):
    post = cursor.execute(""" SELECT * FROM posts WHERE id = %s; """,(id,)).fetchone()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    return {"data": post} 

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT) #204 when sth is deleted
def deletePost(id: int):
    post = cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING *;""",(id,)).fetchone()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def updatePost(id:int, post: Post): #with the PUT we need all the field
    updatedPost = cursor.execute(""" UPDATE posts SET title = %s , content = %s , published = %s WHERE id = %s RETURNING *;""", (post.title,post.content,post.published,id)).fetchone()
    if updatedPost == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    conn.commit()
    return{"data": updatedPost}





