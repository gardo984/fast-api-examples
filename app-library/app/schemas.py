
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class AuthorCreate(BaseModel):
    name: str
    email: EmailStr  # Use EmailStr for email validation
    age: int
    active: Optional[bool] = True  # Optional, with a default value


# Pydantic model for returning an Author (output response)
class AuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    name: str
    email: EmailStr
    age: int
    active: bool
