import json
from turtle import update
import pytest
from app import schemas

def test_allPosts(authClient, postsTest):
    res = authClient.get("/posts")
    assert res.status_code == 200
    assert len(postsTest) == len(res.json())
    # get a list of ResponsePost from the output 
    posts = [schemas.ResponsePost(**data) for data in res.json()]
    # sort the list using the id of the post as key
    posts = sorted(posts, key=lambda x: x.Post.id)
    for i in range(len(postsTest)):
        assert posts[i].Post.title == postsTest[i].title
        assert posts[i].Post.content == postsTest[i].content
        assert posts[i].Post.user_id == postsTest[i].user_id

def test_unAuth_allPosts(client):
    #we use the unauthorized cient to do this
    res = client.get("/posts")
    assert res.status_code == 401

def test_singlePost(authClient, postsTest):
    for i in range(len(postsTest)):
        res = authClient.get(f"/posts/{postsTest[i].id}")
        assert res.status_code == 200
        singlePost = schemas.ResponsePost(**res.json())
        assert postsTest[i].id == singlePost.Post.id
        assert postsTest[i].title == singlePost.Post.title
        assert postsTest[i].content == singlePost.Post.content
        assert postsTest[i].user_id == singlePost.Post.user_id
        assert postsTest[i].created_at == singlePost.Post.created_at
        assert postsTest[i].published == singlePost.Post.published

def test_unAuth_singlePost(client, postsTest):
    for i in range(len(postsTest)):
        res = client.get(f"/posts/{postsTest[i].id}")
        assert res.status_code == 401

def test_notExistingSinglePost(authClient, postsTest):
    res = authClient.get(f"/posts/{2346}")
    assert res.status_code == 404
    assert res.json().get('detail') == f"Post with id {2346} does not exist"

@pytest.mark.parametrize("postData",[
                         {"title": "test title","content": "test comment","published":True,},
                         {"title": "","content": "test comment","published":True,},
                         {"title": "test title","content": "","published":True,},
                         {"title": "test title","content": "test comment","published":False,},
                         {"title": "test title","content": "test comment"},
                         ])
def test_createPost(authClient, userTest, postData):
    res = authClient.post("/posts", json=postData)
    assert res.status_code == 201
    # use the schema to validate the response of the user creation
    newPost = schemas.PostOut(**res.json())
    assert postData["title"] == newPost.title
    assert postData["content"] == newPost.content
    if "published" in postData.keys():
        assert postData["published"] == newPost.published
    else:
        assert newPost.published == True
    assert userTest["id"] == newPost.user_id


@pytest.mark.parametrize("postDataFail",[
                         {"title": "test title","content": "test comment","published":"Ciao",},
                         {"title": "test title","content": "test comment","published":None,},
                         {"title": "","content": None,"published":True,},
                         {"title": None,"content": "","published":True,},
                         ])
def test_createPostFail(authClient, postDataFail):
    res = authClient.post("/posts", json=postDataFail)
    assert res.status_code == 422

def test_unAuth_createPost(client):
    res = client.post("/posts", json={"title": "test title","content": "test comment"})
    assert res.status_code == 401

def test_deletePost(authClient, postsTest):
    postIds = [post.id for post in postsTest]
    for id in postIds:
        res = authClient.delete(f"/posts/{id}")
        assert res.status_code == 204

def test_deletePost_fail(authClient, postsTest):
    res = authClient.delete(f"/posts/{2345}")
    assert res.status_code == 404
    assert res.json().get("detail") == f"Post with id {2345} does not exist"

def test_unAuth_deletePost(client, postsTest):
    postIds = [post.id for post in postsTest]
    for id in postIds:
        res = client.delete(f"/posts/{id}")
        assert res.status_code == 401

def test_deletePost_fromNotOwner(authClient, userTest, postsTest, userTest2, postsTestFromUser2):
    for post in postsTestFromUser2:
        res = authClient.delete(f"/posts/{post.id}")
        assert res.status_code == 403
        assert res.json().get('detail') == "Not authorized to perform requested action"

def test_updatePost(authClient, postsTest):
    updatedPostData = {
        "title" : "update title",
        "content" : "updated content",
        "published" : False
    }
    postIds = [post.id for post in postsTest]
    for id in postIds:
        res = authClient.put(f"/posts/{id}", json=updatedPostData)
        assert res.status_code == 200
        updatedPost = schemas.PostOut(**res.json())
        assert updatedPost.title == updatedPostData["title"]
        assert updatedPost.content == updatedPostData["content"]
        assert updatedPost.published == updatedPostData["published"]

def test_unAuth_updatePost(client, postsTest):
    updatedPostData = {
        "title" : "update title",
        "content" : "updated content",
        "published" : False
    }
    postIds = [post.id for post in postsTest]
    for id in postIds:
        res = client.put(f"/posts/{id}", json=updatedPostData)
        assert res.status_code == 401

def test_deletePost_fromNotOwner(authClient, userTest, postsTest, userTest2, postsTestFromUser2):
    updatedPostData = {
        "title" : "update title",
        "content" : "updated content",
        "published" : False
    }
    for post in postsTestFromUser2:
        res = authClient.put(f"/posts/{post.id}", json=updatedPostData)
        assert res.status_code == 403
        assert res.json().get('detail') == "Not authorized to perform requested action"