from datetime import datetime, timedelta
from typing import Annotated # for dependency injection
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form  # for router and dependency injection, raise exception
from pydantic import BaseModel
from database import SessionLocal , engine
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session 
from starlette import status # for status code
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer # form to get username and password, decode JWT token
from jose import jwt, JWTError # JWT token library
import os
from dotenv import load_dotenv
from typing import Optional
import models
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

templates = Jinja2Templates(directory="templates")



load_dotenv()




router = APIRouter(
    prefix='/auth',
    tags=['auth'], #no todoapp esta auth minicusculo default esta A maisculo vou trocar caso de problema estava Auth
    responses={401: {"user": "Not authorized"}}
)


SECRET_KEY=os.getenv("AUTH_SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM") # algorithm to encode JWT token

class LoginForm:
    def __init__(self, request:Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")

models.Base.metadata.create_all(bind=engine)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto') # hash password
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token') # get token from url to authenticate user


def get_password_hash(password):
    return bcrypt_context.hash(password)
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
async def get_current_user(request: Request, token: Annotated[str, Depends(oauth2_bearer)]):
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
            logout(request)
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="Not Found")
    #         raise credentials_exception
    #     return {'username': username, 'id': user_id, 'user_role': user_role}
    # except JWSError:
    #     raise credentials_exception

    
#Endpoints
# endpoint to create user




# @router.post('/', status_code=status.HTTP_201_CREATED)
# async def create_user(db: db_dependency,
#                       create_user_request: CreateUserRequest):
#     create_user_model = Users(
#         email=create_user_request.email,
#         username=create_user_request.username,
#         first_name=create_user_request.first_name,
#         last_name=create_user_request.last_name,
#         role=create_user_request.role,
#         hashed_password=bcrypt_context.hash(create_user_request.password),
#         is_activate=True
#     )
    
#     db.add(create_user_model)
#     db.commit()
#     db.refresh(create_user_model)

# endpoint to get token
@router.post("/token", response_model=token)
async def login_for_access_token(response: Response, form_data: Annotated[ OAuth2PasswordRequestForm, Depends()], 
                                 db: db_dependency):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'})
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username, user.id, user.role, expires_delta=token_expires)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/docs", status_code=status.HTTP_302_FOUND)
        
        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)
        if not validate_user_cookie:
            msg = "Invalid username or password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        return response
    except HTTPException:
        msg = "Invalid username or password"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    
@router.get("/logout")
async def logout(request: Request):
    msg="Logout Successful"
    response = templates.TemplateResponse("login.html",{"request":request, "msg":msg})
    response.delete_cookie(key="access_token")
    return response 

@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html",{"request": request})
@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request,email : str = Form(...), username : str = Form(...),
                        firstname: str = Form(...), lastname: str = Form(...), password: str = Form(...),
                        password2: str = Form(...), db: Session = Depends(get_db)):
    validation1 = db.query(models.Users).filter(models.Users.username == username).first()

    validation2 = db.query(models.Users).filter(models.Users.email == email).first()

    if password != password2 or validation1 is not None or validation2 is not None:
        msg="Solicitação de Registro inválida" 
        return templates.TemplateResponse("register.html",{"request":request, "msg": msg})
    user_model = models.Users()
    user_model.username = username
    user_model.email = email
    user_model.first_name = firstname
    user_model.last_name = lastname

    hash_password = get_password_hash(password)
    user_model.hashed_password = hash_password
    user_model.is_active = True

    db.add(user_model)
    db.commit()

    msg="Usuario Criado com Sucesso" 
    return templates.TemplateResponse("login.html",{"request":request, "msg": msg})