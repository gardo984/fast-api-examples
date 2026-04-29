from typing import List, Dict, Optional, Union
from fastapi import (
    Request, Response, status, HTTPException,
    Depends,
    APIRouter,
)
from sqlalchemy.orm import Session
from app.schemas import (
    AuthorCreate,
    AuthorUpdate,
    AuthorResponse,
)

from app.db.database import get_db, engine
from app.db.models import (
    Base,
    Author,
    User,
)
from app.oauth2 import get_current_active_user


router = APIRouter(
    tags=["Authors"]
)


@router.get(
    "/author/",
    status_code=status.HTTP_200_OK,
    response_model=List[AuthorResponse],
)
async def author_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"querystring: {dict(request.query_params)}")
    authors = db.query(Author).all()
    return authors


@router.get(
    "/author/{author_id}",
    status_code=status.HTTP_200_OK,
    response_model=AuthorResponse,
)
async def author_by_id(
    request: Request,
    author_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
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


@router.post(
    "/author/",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[AuthorResponse, List[AuthorResponse]],
)
async def author_create(
    request: Request,
    payload: Union[AuthorCreate | List[AuthorCreate]],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    print(f"Url: {request.url}, method: {request.method}")
    authors_to_create: List[Author] = []
    if not isinstance(payload, List):
        payload = [payload]

    decoded_data = [item.model_dump() for item in payload]
    print(f"Payload: {decoded_data}")
    for author_data in payload:
        db_author = Author(
            name=author_data.name,
            email=author_data.email,
            age=author_data.age,
            active=author_data.active,
            created_by_id=current_user.id,
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


@router.put(
    "/author/{author_id}",
    status_code=status.HTTP_200_OK,
    response_model=AuthorResponse,
)
async def author_update(
    request: Request,
    author_id: int,
    payload: AuthorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"Payload: {payload.model_dump()}")
    author = db.query(Author).where(Author.id == author_id).first()
    if not author:
        print(f"Author does not exist authorId: {author_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author does no exist",
        )

    update_data = payload.model_dump()
    for key, value in update_data.items():
        setattr(author, key, value)

    # other option
    # author = db.query(Author).where(Author.id == author_id)
    # author.update(update_data, synchronize_session=False)

    db.commit()
    db.refresh(author)
    print(f"Author successfully updated authorId:{author_id}")
    return author


@router.delete(
    "/author/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def author_delete(
    request: Request, author_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
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
