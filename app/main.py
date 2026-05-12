from fastapi import FastAPI
from .database import Base, engine
from . import models
from .routes import pdf_routes, auth_routes, chat_routes

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_routes.router)
app.include_router(pdf_routes.router)
app.include_router(chat_routes.router)


@app.get("/")
def index():
    return {"message":"Welcome to AI Assistent"}