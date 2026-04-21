from typing import List, Dict, Optional, Union
from fastapi import (
    FastAPI, Request, Response, status, HTTPException,
    Depends,
)
from faker import Faker
# from fastapi.params import Body
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .db.database import get_db, engine
from .db.models import (
    Base,
    Author,
    User,
)
from .schemas import (
    AuthorCreate,
    AuthorUpdate,
    AuthorResponse,
    UserResponse,
    UserCreate,
)

Base.metadata.create_all(bind=engine)

app = FastAPI()
fake = Faker()


@app.get(
    "/author",
    status_code=status.HTTP_200_OK,
    response_model=List[AuthorResponse],
)
async def author_list(
    request: Request,
    db: Session = Depends(get_db),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"querystring: {dict(request.query_params)}")
    authors = db.query(Author).all()
    return authors


@app.get(
    "/author/{author_id}",
    status_code=status.HTTP_200_OK,
    response_model=AuthorResponse,
)
async def author_by_id(
    request: Request,
    author_id: int,
    db: Session = Depends(get_db),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"Path args author_id: {author_id}")
    author = db.query(Author).where(Author.id == author_id).one_or_none()
    if not author:
        print(f"Author does not exist authorId={author_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author does not exist",
        )
    return author


@app.post(
    "/author/",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[AuthorResponse, List[AuthorResponse]],
)
async def author_create(
    request: Request,
    payload: Union[AuthorCreate | List[AuthorCreate]],
    db: Session = Depends(get_db),
):
    print(f"Url: {request.url}, method: {request.method}")
    authors_to_create: List[Author] = []
    if not isinstance(payload, List):
        payload = [payload]

    decoded_data = [item.dict() for item in payload]
    print(f"Payload: {decoded_data}")
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


@app.put(
    "/author/{author_id}",
    status_code=status.HTTP_200_OK,
    response_model=AuthorResponse,
)
async def author_update(
    request: Request,
    author_id: int,
    payload: AuthorUpdate,
    db: Session = Depends(get_db),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"Payload: {payload.dict()}")
    author = db.query(Author).where(Author.id == author_id).first()
    if not author:
        print(f"Author does not exist authorId: {author_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author does no exist",
        )

    update_data = payload.dict()
    for key, value in update_data.items():
        setattr(author, key, value)

    # other option
    # author = db.query(Author).where(Author.id == author_id)
    # author.update(update_data, synchronize_session=False)

    db.commit()
    db.refresh(author)
    print(f"Author successfully updated authorId:{author_id}")
    return author


@app.delete(
    "/author/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def author_delete(
    request: Request, author_id: int, db: Session = Depends(get_db),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"Path args author_id: {author_id}")

    author = db.query(Author).where(Author.id == author_id).first()
    if not author:
        print(f"Author does not exist authorId:{author_id}")
        raise HTTPException(
            detail=f"Book does not exist",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    db.delete(author)
    db.commit()
    print(f"Author removed successfully authorId:{author_id}")
    return {}


# users

@app.post(
    "/users/",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[UserResponse, List[UserResponse]],
)
async def user_create(
    request: Request,
    payload: Union[UserCreate | List[UserCreate]],
    db: Session = Depends(get_db),
):
    print(f"Url: {request.url}, method: {request.method}")
    users_to_create: List[User] = []
    if not isinstance(payload, List):
        payload = [payload]

    decoded_data = [item.dict() for item in payload]
    print(f"Payload: {decoded_data}")
    user_list = list(set([x.email.lower() for x in payload]))
    user_exists = User.validate_users_existence(db, user_list)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Users already registered: {','.join(user_exists)}"
        )

    created_users: List[User] = User.create_users(db=db, users=payload)
    return created_users


@app.get(
    "/users/",
    status_code=status.HTTP_200_OK,
    response_model=List[UserResponse],
)
async def user_list(
    request: Request,
    db: Session = Depends(get_db),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"querystring: {dict(request.query_params)}")
    users = db.query(User).all()
    return users


@app.get(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def user_by_id(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"Path args user_id: {user_id}")
    user = db.query(User).where(User.id == user_id).one_or_none()
    if not user:
        print(f"User does not exist userId={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )
    return user


@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def user_delete(
    request: Request, user_id: int, db: Session = Depends(get_db),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"Path args user_id: {user_id}")

    user = db.query(User).where(User.id == user_id)
    if not user.first():
        print(f"User does not exist userId:{user_id}")
        raise HTTPException(
            detail=f"User does not exist",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    user_email = user.email
    user.delete(synchronize_session=False)
    db.commit()
    print(f"User removed successfully userId:{user_id}, email={user_email}")
    return {}
