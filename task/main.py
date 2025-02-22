from fastapi import FastAPI
from .routers import upload, getfile, addTask, get_status
from .database import engine
from . import models

app = FastAPI()

models.Base.metadata.create_all(engine)




app.include_router(upload.router)
app.include_router(getfile.router)
app.include_router(addTask.router)