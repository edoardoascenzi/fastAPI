import json
from turtle import title
from fastapi.testclient import TestClient
import pytest
from app.main import app

from sqlalchemy.orm import sessionmaker
from app.config import settings
from sqlalchemy import create_engine
from app.database import get_db, Base

from app.oauth2 import createAccessToken

from app import models

#here we call the test db fastapi_test, in this way we can just add _test to the dev URL
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

## DATABASE FIXTURE
@pytest.fixture
def sessionDB():
    Base.metadata.drop_all(bind=engine) 
    Base.metadata.create_all(bind=engine) 
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(sessionDB):
    def get_test_db():
        db = sessionDB
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)


## USER FIXTURE
    
@pytest.fixture
def userTest(client):
    userData = {
    "email" : "hello123@gmail.com",
    "password" : "password123"
    }
    res = client.post("/users", json=userData)
    assert res.status_code == 201
    out = userData.copy()
    out["id"] = res.json()["id"]
    return out

@pytest.fixture
def userTest2(client):
    userData = {
    "email" : "user2@gmail.com",
    "password" : "password123"
    }
    res = client.post("/users", json=userData)
    assert res.status_code == 201
    out = userData.copy()
    out["id"] = res.json()["id"]
    return out

#use the createAccessToken feature instead of using the whole API path to authorize
@pytest.fixture
def token(client,userTest):
    return createAccessToken(data={'user_id': userTest["id"]})

#client that has been already authenticated
@pytest.fixture
def authClient(client, token):
    #add the token in the same way tou are using in postman
    client.headers = {
        "Authorization" : f"Bearer {token}"
    }
    return client

## POST FIXTURE

@pytest.fixture
def postsTest(userTest, sessionDB):
    postsData = [{
        "title": "first title",
        "content": "first content",
        "user_id": userTest['id']
    }, {
        "title": "2nd title",
        "content": "2nd content",
        "user_id": userTest['id']
    },
        {
        "title": "3rd title",
        "content": "3rd content",
        "user_id": userTest['id']
    }, {
        "title": "3rd title",
        "content": "3rd content",
        "user_id": userTest['id']
    }] 
    
    #lambda function that create the single post from the single dict structure
    createPostModel = lambda data: models.Post(**data)
    #create a list of post obj by using a map with the lambda function and the list of dict
    postList = list(map(createPostModel, postsData))

    sessionDB.add_all(postList)
    sessionDB.commit()
    res = sessionDB.query(models.Post).order_by(models.Post.id).filter(models.Post.user_id == userTest['id']).all()
    #this is actually a post object with everything
    return res

@pytest.fixture
def postsTestFromUser2(userTest2, sessionDB):
    postsData = [{
        "title": "first title of user2",
        "content": "first content",
        "user_id": userTest2['id']
    }, {
        "title": "2nd title of user2",
        "content": "2nd content",
        "user_id": userTest2['id']
    }] 
    #lambda function that create the single post from the single dict structure
    createPostModel = lambda data: models.Post(**data)
    #create a list of post obj by using a map with the lambda function and the list of dict
    postList = list(map(createPostModel, postsData))

    sessionDB.add_all(postList)
    sessionDB.commit()
    res = sessionDB.query(models.Post).order_by(models.Post.id).filter(models.Post.user_id == userTest2['id']).all()

    #this is actually a post object with everything
    return res


    
