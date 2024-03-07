import pytest
from app import models
from sqlalchemy import func

def test_likeAndUnlikeOnPost(authClient, sessionDB, postsTestFromUser2, userTest):
    voteData = {
        "post_id":postsTestFromUser2[0].id,
        "direction": 1,
    }
    #vote on a post
    res = authClient.post("/vote", json=voteData)
    assert res.status_code == 201

    #query the votes table
    votes = sessionDB.query(models.Vote).all()
    #check there is only one vote
    assert len(votes) == 1
    #unpack the vote
    vote = votes[0]
    assert vote.post_id == voteData["post_id"]
    assert vote.user_id == userTest["id"]

    #query the post joined with the vote table 
    post = sessionDB.query(models.Post, func.count(models.Vote.post_id).label("likes")).join(models.Vote , models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id)
    post = post.filter(models.Post.id == voteData["post_id"]).first()
    #check the number of likes increased by one
    assert post.likes == 1

    #change the direction of the vote
    voteData["direction"] = 0

    #unlike the post
    res = authClient.post("/vote", json=voteData)
    assert res.status_code == 204

    #query the votes table again
    votes = sessionDB.query(models.Vote).all()
    #check there is only no votes
    assert len(votes) == 0

    #query again the voted post
    post = sessionDB.query(models.Post, func.count(models.Vote.post_id).label("likes")).join(models.Vote , models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id)
    post = post.filter(models.Post.id == voteData["post_id"]).first()
    #check the number of likes decreased by one
    assert post.likes == 0

def test_unAuth_likeAndUnlikeOnPost(client, postsTestFromUser2):
    voteData = {
        "post_id":postsTestFromUser2[0].id,
        "direction": 1,
    }
    #vote on a post
    res = client.post("/vote", json=voteData)
    assert res.status_code == 401

    #change the direction of the vote
    voteData["direction"] = 0

    #unlike the post
    res = client.post("/vote", json=voteData)
    assert res.status_code == 401


def test_fail_unlikeWithoutLikePost(authClient,postsTestFromUser2, userTest):
    voteData = {
        "post_id":postsTestFromUser2[0].id,
        "direction": 0
    }
    #unvote on a post without likes
    res = authClient.post("/vote", json=voteData)
    assert res.status_code == 403
    assert res.json().get('detail') == f"User {userTest['id']} does not like post {voteData['post_id']}"

def test_fail_doubleLikePost(authClient,postsTestFromUser2, userTest):
    voteData = {
        "post_id":postsTestFromUser2[0].id,
        "direction": 1
    }
    #vote on a post
    res = authClient.post("/vote", json=voteData)
    assert res.status_code == 201
    #vote again on the same post
    res = authClient.post("/vote", json=voteData)
    assert res.status_code == 409
    assert res.json().get('detail') == f"User {userTest['id']} already like post {voteData['post_id']}"

def test_fail_likeOnNotExistigPost(authClient,postsTestFromUser2, userTest):
    voteData = {
        "post_id":2345,
        "direction": 1
    }
    #unvote on a post without likes
    res = authClient.post("/vote", json=voteData)
    assert res.status_code == 404
    assert res.json().get('detail') == f"Post {voteData['post_id']} does not exist"

def test_fail_likeOnYourOwnPost(authClient,postsTest, userTest):
    voteData = {
        "post_id":postsTest[0].id,
        "direction": 1
    }
    #unvote on a post without likes
    res = authClient.post("/vote", json=voteData)
    assert res.status_code == 403
    assert res.json().get('detail') == "Can not like your own posts!"