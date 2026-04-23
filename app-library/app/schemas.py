
from datetime import datetime
from typing import Optional, Dict
from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    field_serializer,
    model_serializer,
    field_validator,
    SerializerFunctionWrapHandler,
    Field,
)


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

    @field_serializer('created_at')
    def date_format(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %T")

    @model_serializer(mode="wrap")
    def serialize_model(
        self, handler: SerializerFunctionWrapHandler
    ) -> Dict[str, object]:
        serialized_data = handler(self)
        return serialized_data


class Book(BaseModel):
    name: str
    category: str
    year: int
    published: bool = True
    expired: Optional[bool] = False

# users


class UserBase(BaseModel):
    email: EmailStr  # Use EmailStr for email validation

    @field_validator("email", mode="before")
    @classmethod
    def lowercase(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=100)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

    @field_serializer('created_at')
    def date_format(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %T")

    @model_serializer(mode="wrap")
    def serialize_model(
        self, handler: SerializerFunctionWrapHandler
    ) -> Dict[str, object]:
        serialized_data = handler(self)
        return serialized_data


class LoginCredentials(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class LoginResponse(BaseModel):
    access_token: str