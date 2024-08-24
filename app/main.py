from fastapi import FastAPI
from .database import engine, Base
from .api import endpoints

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(endpoints.router)
