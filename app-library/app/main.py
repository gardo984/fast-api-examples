import json
from typing import List, Dict, Optional, Union
from fastapi import (
    FastAPI, Request, Response, status, HTTPException,
    Depends,
)
# from faker import Faker
# from fastapi.params import Body
from pydantic import BaseModel
from .db.models import Base
from .db.database import engine

from .router import (
    users, authors, auth,
)
from .config import Settings

Base.metadata.create_all(bind=engine)

app = FastAPI()
# fake = Faker()

app.include_router(users.router)
app.include_router(authors.router)
app.include_router(auth.router)


@app.get("/")
def main():
    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps(dict(msg="App Library API Interface")),
        media_type="application/json",
    )
