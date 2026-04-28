from typing import List, Dict, Optional, Union
from fastapi import (
    Request, Response, status, HTTPException,
    Depends,
    APIRouter,
)
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from app.schemas import (
    BookCreate,
    BookUpdate,
    BookResponse,
)

from app.db.database import get_db, engine
from app.db.models import (
    Base,
    Book,
    Category,
    User,
    Author,
)
from app.oauth2 import get_current_active_user


router = APIRouter(
    prefix="/books",
    tags=["Books"]
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[BookResponse],
)
async def book_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 10,
    offset: int = 0,
    sorted_by: str = "id",
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"querystring: {dict(request.query_params)}")

    if sorted_by not in inspect(Book).columns:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid sorted field: {sorted_by}",)

    sorted_field = getattr(Book, sorted_by)
    books = (
        db.query(Book).order_by(sorted_field)
        .limit(limit).offset(offset)
    )
    return books


@router.get(
    "/{book_id}",
    status_code=status.HTTP_200_OK,
    response_model=BookResponse,
)
async def book_by_id(
    request: Request,
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"Path args book_id: {book_id}")
    instance = db.query(Book).where(Book.id == book_id).one_or_none()
    if not instance:
        print(f"Book does not exist bookId={book_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book does not exist",
        )
    return instance


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[BookResponse, List[BookResponse]],
)
async def book_create(
    request: Request,
    payload: Union[BookCreate | List[BookCreate]],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    print(f"Url: {request.url}, method: {request.method}")
    items_to_create: List[Book] = []
    if not isinstance(payload, List):
        payload = [payload]

    decoded_data = [item.dict() for item in payload]
    print(f"Payload: {decoded_data}")
    for item in payload:
        category_instance = Category.validate_existence(item.category_id, db)
        author_instance = Author.validate_existence(item.author_id, db)
        if not category_instance:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Invalid category_id: {category_id}")

        if not author_instance:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Invalid author_id: {author_id}",)

        db_instance = Book(
            name=item.name,
            active=item.active,
            category_id=item.category_id,
            author_id=item.author_id,
            created_by_id=current_user.id,
        )
        db.add(db_instance)
        items_to_create.append(db_instance)

    db.commit()
    for item in items_to_create:
        db.refresh(item)

    return (
        items_to_create if len(items_to_create) > 1
        else items_to_create[0]
    )


@router.put(
    "/{book_id}",
    status_code=status.HTTP_200_OK,
    response_model=BookResponse,
)
async def book_update(
    request: Request,
    book_id: int,
    payload: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"Payload: {payload.dict()}")
    instance = db.query(Book).where(Book.id == book_id).first()
    if not instance:
        print(f"Book does not exist bookId: {book_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book does no exist",
        )

    update_data = payload.dict()
    for key, value in update_data.items():
        setattr(instance, key, value)

    # other option
    # instance = db.query(Book).where(Book.id == book_id)
    # instance.update(update_data, synchronize_session=False)

    db.commit()
    db.refresh(instance)
    print(f"Book successfully updated bookId:{book_id}")
    return instance


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def book_delete(
    request: Request, book_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"Path args book_id: {book_id}")

    instance = db.query(Book).where(Book.id == book_id).first()
    if not instance:
        print(f"Book does not exist bookId:{book_id}")
        raise HTTPException(
            detail=f"Book does not exist",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    db.delete(instance)
    db.commit()
    print(f"Book removed successfully bookId:{book_id}")
    return {}
