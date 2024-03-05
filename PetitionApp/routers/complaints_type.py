from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from fastapi import Depends, HTTPException, Path, APIRouter
from models import Complaint_Type
from database import SessionLocal
from starlette import status
from .auth import get_current_user


router = APIRouter(
    prefix='/complaint_types',
    tags=['Complaint Types']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
          
class ComplaintRequest(BaseModel):
    complaint_type: int
    dictionary: str

@router.get('/', status_code=status.HTTP_200_OK)
async def read_all_complaint_types(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Complaint_Type).all()


@router.get('/{complaint_type_id}', status_code=status.HTTP_200_OK)
async def read_complaint_type_by_id(user: user_dependency, db: db_dependency, complaint_type_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
     
    complaint_model = db.query(Complaint_Type).filter(Complaint_Type.id == complaint_type_id).first()
    if complaint_model is not None:
        return complaint_model
    raise HTTPException(status_code=404, detail='Complaint type not found')


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_complaint_type(db: db_dependency, user: user_dependency, complaint_request: ComplaintRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    complaint_model = Complaint_Type(**complaint_request.model_dump()) 
    
    db.add(complaint_model)
    db.commit()
    db.refresh(complaint_model)
    return complaint_model


@router.put('/{complaint_type_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_complaint_type_by_id(user: user_dependency, db: db_dependency, complaint_request: ComplaintRequest, complaint_type_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    complaint_model = db.query(Complaint_Type).filter(Complaint_Type.id == complaint_type_id).first()
    if complaint_model is None:
        raise HTTPException(status_code=404, detail='Signature not found')
    
    complaint_model.complaint_type = complaint_request.complaint_type # type: ignore
    complaint_model.dictionary = complaint_request.dictionary # type: ignore

    db.add(complaint_model)
    db.commit() 


@router.delete('/{complaint_type_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_complaint_type_by_id(user: user_dependency, db: db_dependency, complaint_type_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    signature_model = db.query(Complaint_Type).filter(Complaint_Type.id == complaint_type_id).first()
    if signature_model is None:
        raise HTTPException(status_code=404, detail='Signature not found')
    db.query(Complaint_Type).filter(Complaint_Type.id == complaint_type_id).delete()
    db.commit()

