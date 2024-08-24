from fastapi import FastAPI
from .database import engine
from .models import Base
from .api import endpoints

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(endpoints.router)
