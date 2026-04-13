from typing import List, Dict, Optional
from fastapi import FastAPI
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


@app.get("/books")
async def books_list():
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

@app.get("/books/{book_id}")
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

@app.post("/books/")
async def books_create_item(payload: Book):
    print(f"Payload: {payload.dict()}")
    items: Dict = payload.dict()
    items.update({
        "book_id": fake.random_int(min=1, max=100),
    })
    return {
        "ok": True,
        "message": "Book successfully created",
        "data": items
    }
