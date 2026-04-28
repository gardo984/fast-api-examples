
from typing import List, Dict, Optional, Union
from fastapi import (
    Request, Response, status, HTTPException,
    Depends,
    APIRouter,
)
from sqlalchemy.orm import Session
from app.schemas import (
    UserCreate,
    UserResponse,
)

from app.db.database import get_db, engine
from app.db.models import (
    Base,
    User,
)
from app.oauth2 import get_current_active_user


router = APIRouter(
    tags=["Users"]
)
# users


@router.post(
    "/users/",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[UserResponse, List[UserResponse]],
)
async def user_create(
    request: Request,
    payload: Union[UserCreate | List[UserCreate]],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
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

    created_users: List[User] = User.create_users(
        db=db, users=payload, current_user=current_user,
    )
    return created_users


@router.get(
    "/users/",
    status_code=status.HTTP_200_OK,
    response_model=List[UserResponse],
)
async def user_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"querystring: {dict(request.query_params)}")
    users = db.query(User).all()
    return users


@router.get(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def user_by_id(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
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


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def user_delete(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
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
