from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from fastapi import Depends, HTTPException, Path, APIRouter
from models import Petition
from database import SessionLocal
from starlette import status
from .auth import get_current_user


router = APIRouter(
    prefix='/petitions',
    tags=['Petitions']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class PetitionRequest(BaseModel):
    petition_name: str = Field(min_length=3)
    petition_text: str = Field(min_length=3, max_length=100)
    user_id: int = Field(gt=0, lt=600)
    image: str = Field(min_lenght=1)
          

@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Petition).filter(Petition.user_id == user.get('id')).all()


@router.get('/{petition_id}', status_code=status.HTTP_200_OK)
async def read_petition_by_id(user: user_dependency, db: db_dependency, petition_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
     
    petition_model = db.query(Petition).filter(Petition.id == petition_id).filter(Petition.user_id == user.get('id')).first()
    if petition_model is not None:
        return petition_model
    raise HTTPException(status_code=404, detail='Petition not found')


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_petition(user: user_dependency, db: db_dependency, petition_request: PetitionRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    petition_model = PetitionRequest(**petition_request.model_dump(), owner_id=user.get('id'))
    
    db.add(petition_model)
    db.commit()
    db.refresh(petition_model)
    return petition_model


@router.put('/{petition_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_petition_by_id(user: user_dependency, db: db_dependency, petition_request: PetitionRequest, petition_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    petition_model = db.query(Petition).filter(Petition.id == petition_id).filter(Petition.owner_id == user.get('id') ).first()
    if petition_model is None:
        raise HTTPException(status_code=404, detail='Petition not found')
    
    petition_model.petition_name = petition_request.petition_name # type: ignore
    petition_model.petition_text = petition_request.petition_text # type: ignore
    petition_model.image = petition_request.image # type: ignore


    db.add(petition_model)
    db.commit() 


@router.delete('/{petition_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_petition_by_id(user: user_dependency, db: db_dependency, petition_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    petition_model = db.query(Petition).filter(Petition.id == petition_id).filter(Petition.owner_id == user.get('id')).first()
    if petition_model is None:
        raise HTTPException(status_code=404, detail='Petition not found')
    db.query(Petition).filter(Petition.id == petition_id).filter(Petition.owner_id == user.get('id')).delete()

    db.commit()


    