from typing import List, Dict, Optional, Union
from fastapi import (
    FastAPI, Request, Response, status, HTTPException,
    Depends,
)
from faker import Faker
#from fastapi.params import Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .db.database import get_db, engine
from .db.models import (
    Base,
    Author,
)
from .schemas import (
    AuthorCreate,
    AuthorResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI()
fake = Faker()

class Book(BaseModel):
    name: str
    category: str
    year: int
    published: bool = True
    expired: Optional[bool] = False


@app.get("/author", status_code=status.HTTP_200_OK)
async def author_list(request: Request):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"querystring: {dict(request.query_params)}")
    items: List = [
        dict(
            name=fake.name(),
            category=fake.currency_name(),
            year=fake.random_int(min=1900, max=2026),
        )
        for item in range(1, 10)
    ]
    return {
        "data": items
    }

@app.get("/author/{author_id}", status_code=status.HTTP_200_OK)
async def author_get_book(author_id: int):
    items: Dict = dict(
        author_id=author_id,
        name=fake.name(),
        category=fake.currency_name(),
        year=fake.random_int(min=1900, max=2026),
    )
    return {
        "data": items
    }

@app.post(
    "/author/",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[AuthorResponse, List[AuthorResponse]],
)
async def author_create_item(
    request: Request,
    payload: Union[AuthorCreate | List[AuthorCreate]],
    db: Session = Depends(get_db),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"Payload: {payload}")
    authors_to_create: List[Author] = []
    if not isinstance(payload, List):
        payload = [payload]

    for author_data in payload:
        db_author = Author(
            name=author_data.name,
            email=author_data.email,
            age=author_data.age,
            active=author_data.active,
        )
        db.add(db_author)
        authors_to_create.append(db_author)

    db.commit()
    for author in authors_to_create:
        db.refresh(author)

    if len(authors_to_create) > 1:
        return authors_to_create
    else:
        return authors_to_create[0]


@app.delete("/author/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def author_delete(
    request: Request,
    response: Response,
    author_id: int
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"BookId: {author_id}")

    message = f"Book {author_id} was removed successfully"
    # hardcoding condition for testing purposes
    if author_id == 10:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # message = "Book does not exist"
        raise HTTPException(
            detail=f"Book does not exist",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return {"message": message}
