#SECRET_KEY
#Algorithm
#Expiration Time

from fastapi import Depends, status, HTTPException
from jose import JWTError, jwt, ExpiredSignatureError
from datetime import datetime,timedelta,timezone
from . import schemas, database,models,schemas
from sqlalchemy.orm import Session

from .config import settings

from fastapi.security.oauth2 import OAuth2PasswordBearer
oauthScheme = OAuth2PasswordBearer(tokenUrl="login") #

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def createAccessToken(data:dict) -> str:
    toEncode = data.copy() #copy the received data (in order not to change them)
    expireTime = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) #evaluate the expiration time
    toEncode.update({'exp': expireTime}) # add the expiration time to the data

    encodedJWT = jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)

    return encodedJWT

def verifyAccessToken(accessToken: str, exceptions) -> dict:
    try:
        #decode the accessToken that come from the client
        payload = jwt.decode(accessToken, SECRET_KEY, algorithms=[ALGORITHM])
        #extract the info of it
        user_id: str = payload.get('user_id')
        #check the correct validation of it
        if user_id == None:
            raise exceptions['credentials']
        tokenData = schemas.TokenData(user_id = user_id)

    except ExpiredSignatureError:
        raise exceptions['expiredToken']
    except JWTError:
        raise exceptions['credentials']
    
    return tokenData

def getCurrentUser(accessToken: str = Depends(oauthScheme), db : Session = Depends(database.get_db)):
    """
    This function will be passed as dependency to our API fuction 
    It will automatically decode the token, validate it, and return the id of the user
    in order to be fatched
    """
    exceptions = {
        'credentials': HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}),
        'expiredToken': HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Session Expired", headers={"WWW-Authenticate": "Bearer"}),
    }
    tokenData = verifyAccessToken(accessToken, exceptions)
    currentUser = db.query(models.User).filter(models.User.id == tokenData.user_id).first()
    return currentUser




