from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = "ProfOgAPI"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
ACCESS_TOKEN_EXPIRE_MINUTES_FOR_OTP=300

def create_access_token(data: dict,exp_date = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=exp_date)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(encoded_jwt)
    return encoded_jwt

def create_access_token_for_otp(data: dict,exp_date = ACCESS_TOKEN_EXPIRE_MINUTES_FOR_OTP):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=exp_date)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(encoded_jwt)
    return encoded_jwt

def create_access_token_for_registration(data: dict,exp_date = ACCESS_TOKEN_EXPIRE_MINUTES_FOR_OTP):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=exp_date)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(encoded_jwt)
    return encoded_jwt

def get_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_phone")
        print(id)
        if id is None:
            raise credentials_exception
        # token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return id

def get_data(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return payload
