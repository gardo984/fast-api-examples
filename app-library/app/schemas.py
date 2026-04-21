
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class AuthorBase(BaseModel):
    name: str
    email: EmailStr  # Use EmailStr for email validation
    age: int
    active: Optional[bool] = True


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(AuthorCreate):
    pass


class AuthorResponse(AuthorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class Book(BaseModel):
    name: str
    category: str
    year: int
    published: bool = True
    expired: Optional[bool] = False
