from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from fastapi import Depends, HTTPException, Path, APIRouter
from models import Complaint
from database import SessionLocal
from starlette import status
from .auth import get_current_user


router = APIRouter(
    prefix='/complaints',
    tags=['Complaints']
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
    name: str = Field(min_length=3)
    email: str = Field(min_length=5)
    phone: str
    city: str
    state: str
    complaint_type: int
    complaint_text: str

@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Complaint).all()


@router.get('/{complaint_id}', status_code=status.HTTP_200_OK)
async def read_complaint_by_id(user: user_dependency, db: db_dependency, complaint_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
     
    signature_model = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if signature_model is not None:
        return signature_model
    raise HTTPException(status_code=404, detail='Complaint not found')


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_complaint(user: user_dependency, db: db_dependency, complaint_request: ComplaintRequest):
    
    # ----------->  Precisamos de autenticação para registrar uma reclamação/denúncia??
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    # <-----------

    complaint_model = Complaint(**complaint_request.model_dump())
    
    db.add(complaint_model)
    db.commit()
    db.refresh(complaint_model)
    return complaint_model


@router.put('/{complaint_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_complaint_by_id(user: user_dependency, db: db_dependency, complaint_request: ComplaintRequest, complaint_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    complaint_model = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint_model is None:
        raise HTTPException(status_code=404, detail='Complaint not found')
    
    complaint_model.name = complaint_request.name # type: ignore
    complaint_model.email = complaint_request.email # type: ignore
    complaint_model.phone = complaint_request.phone # type: ignore
    complaint_model.city = complaint_request.city
    complaint_model.state = complaint_request.state
    complaint_model.complaint_type = complaint_request.complaint_type
    complaint_model.complaint_text = complaint_request.complaint_text

    db.add(complaint_model)
    db.commit() 


@router.delete('/{complaint_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_complaint_by_id(user: user_dependency, db: db_dependency, complaint_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    complaint_model = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint_model is None:
        raise HTTPException(status_code=404, detail='Complaint not found')
    db.query(Complaint).filter(Complaint.id == complaint_id).delete()
    db.commit()
