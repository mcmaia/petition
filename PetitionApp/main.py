from fastapi import FastAPI
import models
from database import engine
from starlette.staticfiles import StaticFiles
from starlette import status
from starlette.responses import RedirectResponse
from routers import auth, admin, users, petitions, signatures, complaints_type, complaints


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static",StaticFiles(directory="static"),name="static")

@app.get("/")
async def root():
     return RedirectResponse(url="/auth",status_code=status.HTTP_302_FOUND)


app.include_router(auth.router)
app.include_router(petitions.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(signatures.router)
app.include_router(complaints_type.router)
app.include_router(complaints.router)
