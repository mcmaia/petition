from datetime import datetime, timedelta
from typing import Annotated # for dependency injection
from fastapi import APIRouter, Depends, HTTPException # for router and dependency injection, raise exception
from pydantic import BaseModel
from database import SessionLocal # get database
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session 
from starlette import status # for status code
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer # form to get username and password, decode JWT token
from jose import jwt, JWSError # JWT token library
import os
from dotenv import load_dotenv

load_dotenv()


router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


SECRET_KEY=os.getenv("AUTH_SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM") # algorithm to encode JWT token

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto') # hash password
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token') # get token from url to authenticate user

# request model to create user
class CreateUserRequest(BaseModel): 
    username: str
    email: str 
    first_name: str
    last_name: str
    password: str
    role: str
    
# response model to return token
class token(BaseModel): 
    access_token: str
    token_type: str
    
# function to get database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# dependency injection to get database        
db_dependency = Annotated[Session, Depends(get_db)]

#function to authenticate user
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

# function to create JWT token
def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    encoded_jwt = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# verify the current user, it provides security to the endpoints
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub') # type: ignore
        user_id: int = payload.get('id') # type: ignore
        user_role: str = payload.get('role') # type: ignore
        if username is None or user_id is None:
            raise credentials_exception
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWSError:
        raise credentials_exception

    
#Endpoints
# endpoint to create user
@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_activate=True
    )
    
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

# endpoint to get token
@router.post("/token", response_model=token)
async def login_for_access_token(form_data: Annotated[ OAuth2PasswordRequestForm, Depends()], 
                                 db: db_dependency):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'})
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
       raise credentials_exception
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
                                
    return {'access_token': token, 'token_type': 'bearer'}
        