import json
from typing import List, Dict, Optional, Union
from fastapi import (
    FastAPI, Request, Response, status, HTTPException,
    Depends,
)
from fastapi.middleware.cors import CORSMiddleware 
# from faker import Faker
# from fastapi.params import Body
from pydantic import BaseModel
from app.db.models import Base
from app.db.database import engine


from .router import (
    users, authors, auth, books, categories,
)
from app.config import Settings

# actually handled by alembic ORM manager
# Base.metadata.create_all(bind=engine)

app = FastAPI()
# fake = Faker()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://localhost",
    "https://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(authors.router)
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(categories.router)


@app.get("/")
def main():
    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps(dict(msg="App Library API Interface")),
        media_type="application/json",
    )
