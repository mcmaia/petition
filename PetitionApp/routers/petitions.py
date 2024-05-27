# import sys
# sys.path.append("..")
from typing import Optional
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from fastapi import FastAPI
import models

from fastapi import Depends, HTTPException, Path, APIRouter, Request
from models import Petition
from database import engine, SessionLocal
from starlette import status
from .auth import get_current_user

from fastapi.responses import RedirectResponse, JSONResponse, PlainTextResponse, FileResponse, StreamingResponse 
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates



router = APIRouter(
    prefix='/petitions',
    tags=['Petitions'],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/",response_class=HTMLResponse)
async def read_all_by_user(request : Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)#adicionar para todas as paginas para quando nao tiver os cookie de login ele sera redirecionado para pagina de login

    petition=db.query(models.Petition).filter(models.Petition.owner_id == user.get("id")).all()
    return templates.TemplateResponse("home.html",{"request":request,"user":user,"petition":petition})

#add router get /

@router.get("/home",response_class=HTMLResponse)
async def add_home(request : Request):
    return templates.TemplateResponse("home.html",{"request": request})


class PetitionRequest(BaseModel):
    petition_name: str = Field(min_length=3)
    petition_text: str = Field(min_length=3, max_length=1000)
    images: str 
          

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
    petition_model = Petition(
        petition_name=petition_request.petition_name,
        petition_text=petition_request.petition_text,
        images=petition_request.images,
        user_id=user.get('id')
    )
    
    db.add(petition_model)
    db.commit()
    db.refresh(petition_model)
    return petition_model


@router.put('/{petition_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_petition_by_id(user: user_dependency, db: db_dependency, petition_request: PetitionRequest, petition_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    petition_model = db.query(Petition).filter(Petition.id == petition_id).filter(Petition.user_id == user.get('id') ).first()
    if petition_model is None:
        raise HTTPException(status_code=404, detail='Petition not found')
    
    petition_model.petition_name = petition_request.petition_name # type: ignore
    petition_model.petition_text = petition_request.petition_text # type: ignore
    petition_model.images = petition_request.images # type: ignore


    db.add(petition_model)
    db.commit() 


@router.delete('/{petition_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_petition_by_id(user: user_dependency, db: db_dependency, petition_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    petition_model = db.query(Petition).filter(Petition.id == petition_id).filter(Petition.user_id == user.get('id')).first()
    if petition_model is None:
        raise HTTPException(status_code=404, detail='Petition not found')
    db.query(Petition).filter(Petition.id == petition_id).filter(Petition.user_id == user.get('id')).delete()

    db.commit()


    