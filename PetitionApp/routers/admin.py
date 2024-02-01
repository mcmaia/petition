from typing import Annotated
from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, Path, APIRouter
from models import Petition, Signature
from database import SessionLocal
from starlette import status
from .auth import get_current_user


router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/petition", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'Admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Petition).all()

@router.get("/signature", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'Admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Signature).all()


@router.delete("/petition/{petition_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_petition(user: user_dependency, db: db_dependency, petition_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'Admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    todo_model = db.query(Petition).filter(Petition.id == petition_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Petition not found')
    db.query(Petition).filter(Petition.id ==  petition_id).delete()

    db.commit()

@router.delete("/signature/{signature_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_petition(user: user_dependency, db: db_dependency, signature_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'Admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    todo_model = db.query(Signature).filter(Signature.id == signature_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Signature not found')
    db.query(Signature).filter(Signature.id ==  signature_id).delete()

    db.commit()
