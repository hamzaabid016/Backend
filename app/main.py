from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .api import endpoints

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
Base.metadata.create_all(bind=engine)

app.include_router(endpoints.router)
