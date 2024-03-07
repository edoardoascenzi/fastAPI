import pytest
from app import schemas
from app import utils, models
from jose import jwt
from app.config import settings


userData = {
    "email" : "hello123@gmail.com",
    "password" : "password123"
    }


def test_root(client):
    res = client.get("/")
    assert res.json()["message"] == "Hello World!"
    assert res.status_code == 200

def test_createUser(client, sessionDB):
    res = client.post("/users", json=userData)
    # use the schema to validate the response of the user creation
    newUser = schemas.ResponseUser(**res.json())
    assert newUser.email == userData["email"]
    assert res.status_code == 201 #201 for created item

    # query the new user to test the password
    newUserPassword = sessionDB.query(models.User).filter(models.User.id == newUser.id).first().password
    assert utils.verify(userData["password"], newUserPassword)

@pytest.mark.parametrize("userDataFail",[
    {"email":"notanemail","password":"password123"},
    # {"email":"email@gmail.com","password":""}, #seems like it can be empty
    {"email":"email@gmail.com","password":None},
    {"email":None,"password":"password123"},
])
def test_fail_createUser(client, userDataFail):
    res = client.post("/users", json=userDataFail)
    assert res.status_code == 422

def test_loginUser(client, userTest):
    #the login request is with the form-data and not with the json format in the body 
    #the email field has to be called as username
    #the client will be called from userTest, so it is not mandatory
    res = client.post("/login", data={"username":userTest["email"], "password":userTest["password"]})
    assert res.status_code == 200

    loginRes = schemas.Token(**res.json())
    assert loginRes.tokenType == "bearer"
    #to test the token decode it
    payload = jwt.decode(loginRes.accessToken, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload.get('user_id') == userTest["id"]

@pytest.mark.parametrize("email, password, status_code, detail", [
    ("wrongemail@gmail.com", userData["password"], 403 , "Invalid Credentials"),
    (userData["email"], "wrongpassword", 403 , "Invalid Credentials"),
    (None, userData["password"], 422 , None),
    (userData["email"], None, 422 , None),
])
def test_loginFail(client, userTest , email, password, status_code, detail):
    res = client.post("/login", data={"username":email, "password":password})
    assert res.status_code == status_code
    if detail != None:
        #test the detail only when we know what they are
        assert res.json().get('detail') == detail





