from typing import List, Dict, Optional, Union
from fastapi import (
    FastAPI, Request, Response, status, HTTPException,
)
from faker import Faker
#from fastapi.params import Body
from pydantic import BaseModel


app = FastAPI()
fake = Faker()

class Book(BaseModel):
    name: str
    category: str
    year: int
    published: bool = True
    expired: Optional[bool] = False


@app.get("/books", status_code=status.HTTP_200_OK)
async def books_list(request: Request):
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

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def books_get_book(book_id: int):
    items: Dict = dict(
        book_id=book_id,
        name=fake.name(),
        category=fake.currency_name(),
        year=fake.random_int(min=1900, max=2026),
    )
    return {
        "data": items
    }

@app.post("/books/", status_code=status.HTTP_201_CREATED)
async def books_create_item(
    request: Request,
    payload: Union[Book | List[Book]]
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"Payload: {payload}")
    items: List = []
    if isinstance(payload, List):
        items = [{
            "book_id": fake.random_int(min=1, max=100),
            **item.dict()
        } for item in payload]
    else:
        items = [{
            "book_id": fake.random_int(min=1, max=100),
            **payload.dict()
        }]

    return {
        "ok": True,
        "message": "Book successfully created",
        "data": items
    }


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def books_delete(
    request: Request,
    response: Response,
    book_id: int
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"BookId: {book_id}")

    message = f"Book {book_id} was removed successfully"
    # hardcoding condition for testing purposes
    if book_id == 10:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # message = "Book does not exist"
        raise HTTPException(
            detail=f"Book does not exist",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return {"message": message}
