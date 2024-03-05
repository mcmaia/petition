from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from fastapi import Depends, HTTPException, Path, APIRouter
from models import Signature
from database import SessionLocal
from starlette import status
from .auth import get_current_user


router = APIRouter(
    prefix='/signatures',
    tags=['Signatures']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class SignatureRequest(BaseModel):
    name: str = Field(min_length=3)
    email: str = Field(min_length=5)
    phone: str
    city: str
    state: str
    show_signature: bool
    petition_id: int
    can_be_contacted: bool
          

@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Signature).filter(Signature.user_id == user.get('id')).all()


@router.get('/{signature_id}', status_code=status.HTTP_200_OK)
async def read_signature_by_id(user: user_dependency, db: db_dependency, signature_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
     
    signature_model = db.query(Signature).filter(Signature.id == signature_id).filter(Signature.user_id == user.get('id')).first()
    if signature_model is not None:
        return signature_model
    raise HTTPException(status_code=404, detail='Signature not found')


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_signature(db: db_dependency, signature_request: SignatureRequest): #, user: user_dependency):
    # É necessário estar autenticado para ASSINAR ALGO? <----------------------------------------------------------------
    # if user is None:
    #     raise HTTPException(status_code=401, detail='Authentication Failed')
    signature_model = Signature(**signature_request.model_dump(), validated_signature = False) #,user_id=user.get('id')) 
    
    db.add(signature_model)
    db.commit()
    db.refresh(signature_model)
    return signature_model


@router.put('/{signature_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_signature_by_id(user: user_dependency, db: db_dependency, signature_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    signature_model = db.query(Signature).filter(Signature.id == signature_id).filter(Signature.user_id == user.get('id') ).first()
    if signature_model is None:
        raise HTTPException(status_code=404, detail='Signature not found')
    
    signature_model.Signature_name = Signature_request.Signature_name # type: ignore
    signature_model.Signature_text = Signature_request.Signature_text # type: ignore
    signature_model.image = Signature_request.image # type: ignore


    db.add(signature_model)
    db.commit() 


@router.delete('/{signature_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_signature_by_id(user: user_dependency, db: db_dependency, signature_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    signature_model = db.query(Signature).filter(Signature.id == signature_id).filter(Signature.user_id == user.get('id')).first()
    if signature_model is None:
        raise HTTPException(status_code=404, detail='Signature not found')
    db.query(Signature).filter(Signature.id == signature_id).filter(Signature.user_id == user.get('id')).delete()
    db.commit()

@router.put('/validate/{signature_id}', status_code=status.HTTP_200_OK)
@router.get('/validate/{signature_id}', status_code=status.HTTP_200_OK) # Added a get method for naked calls
async def update_signature_by_id(db: db_dependency, signature_id: int = Path(gt=0)):

    signature_model = db.query(Signature).filter(Signature.id == signature_id).first()
    if signature_model is None:
        raise HTTPException(status_code=404, detail='Signature not found')
    
    signature_model.validated_signature = True
    db.add(signature_model)
    db.commit() 
    return signature_model.validated_signature
