from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from fastapi import Depends, HTTPException, APIRouter
from models import Users
from database import SessionLocal
from starlette import status
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto') # hash password

class UserRequest(BaseModel):
   password: str
   new_password: str = Field(min_length=6)

@router.get("/", status_code=status.HTTP_200_OK)
async def get_users(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    users = db.query(Users).filter(Users.id == user.get('id')).first()
    return users  


@router.put('/psswrd-change', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_request: UserRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    
    if not bcrypt_context.verify(user_request.password, user_model.hashed_password): # type: ignore
         raise HTTPException(status_code=401, detail='Error while changing the password')
    user_model.hashed_password = bcrypt_context.hash(user_request.new_password) # type: ignore

    db.add(user_model)
    db.commit() 
         