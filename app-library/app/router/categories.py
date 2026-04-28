from typing import List, Dict, Optional, Union
from fastapi import (
    Request, Response, status, HTTPException,
    Depends,
    APIRouter,
)
from sqlalchemy.orm import Session
from app.schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
)

from app.db.database import get_db, engine
from app.db.models import (
    Base,
    Category,
    User,
)
from app.oauth2 import get_current_active_user


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[CategoryResponse],
)
async def category_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"querystring: {dict(request.query_params)}")
    items = db.query(Category).all()
    return items


@router.get(
    "/{category_id}",
    status_code=status.HTTP_200_OK,
    response_model=CategoryResponse,
)
async def category_by_id(
    request: Request,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"Path args category_id: {category_id}")
    instance = db.query(Category).where(Category.id == category_id).one_or_none()
    if not instance:
        print(f"Category does not exist categoryId={category_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category does not exist",
        )
    return instance


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[CategoryResponse, List[CategoryResponse]],
)
async def category_create(
    request: Request,
    payload: Union[CategoryCreate | List[CategoryCreate]],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    print(f"Url: {request.url}, method: {request.method}")
    items_to_create: List[Category] = []
    if not isinstance(payload, List):
        payload = [payload]

    decoded_data = [item.dict() for item in payload]
    print(f"Payload: {decoded_data}")
    for item in payload:
        db_instance = Category(
            name=item.name,
            active=item.active,
            created_by_id=current_user.id,
        )
        db.add(db_instance)
        items_to_create.append(db_instance)

    db.commit()
    for item in items_to_create:
        db.refresh(item)

    if len(items_to_create) > 1:
        return items_to_create
    else:
        return items_to_create[0]


@router.put(
    "/{category_id}",
    status_code=status.HTTP_200_OK,
    response_model=CategoryResponse,
)
async def category_update(
    request: Request,
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"Payload: {payload.dict()}")
    instance = db.query(Category).where(Category.id == category_id).first()
    if not instance:
        print(f"Category does not exist categoryId: {category_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category does no exist",
        )

    update_data = payload.dict()
    for key, value in update_data.items():
        setattr(instance, key, value)

    # other option
    # instance = db.query(Category).where(Category.id == category_id)
    # instance.update(update_data, synchronize_session=False)

    db.commit()
    db.refresh(instance)
    print(f"Category successfully updated categoryId:{category_id}")
    return instance


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def category_delete(
    request: Request,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"Path args category_id: {category_id}")

    instance = db.query(Category).where(Category.id == category_id).first()
    if not instance:
        print(f"Category does not exist categoryId:{category_id}")
        raise HTTPException(
            detail=f"Category does not exist",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    db.delete(instance)
    db.commit()
    print(f"Category removed successfully categoryId:{category_id}")
    return {}
