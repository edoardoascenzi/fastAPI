from typing import List
from .. import models,schemas,utils,oauth2
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..database import get_db
from fastapi import APIRouter

router = APIRouter(
    prefix="/login",
    tags=['Authentication']
)

@router.post('', response_model=schemas.Token)
def login(userLogin: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm retreive a dict composed by username and password, where the username can be whatewer we want (in this case the email)
    user = db.query(models.User).filter(models.User.email == userLogin.username).first()

    if user == None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')
    
    if not utils.verify(userLogin.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')
    
    #create token
    accessToken = oauth2.createAccessToken(data={'user_id': user.id})
    return {'accessToken': accessToken , 'tokenType':'bearer'}

