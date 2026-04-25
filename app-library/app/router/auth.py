
from fastapi import (
    Response, Request, Depends, APIRouter,
    status,
    HTTPException,
)
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..db.models import User
from ..schemas import LoginCredentials, LoginResponse
from ..oauth2 import create_access_token

router = APIRouter(tags=["Authentication"])


@router.post(
    "/login/",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
)
async def login(
    request: Request,
    credentials: LoginCredentials,
    db: Session = Depends(get_db),
):
    print(f"Url: {request.url}, method: {request.method}")
    print(f"Payload: {credentials.dict()}")
    user_exists = User.validate_users_existence(
        db, [credentials.email,]
    )
    if not user_exists:
        print(f"User does not exist: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Credentials",
        )

    instance, outcome = User.authenticate_user(
        db, credentials.email, credentials.password,
    )
    if not outcome:
        print(f"Invalid credentials: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Credentials",
        )
    data = dict(user_id=instance.id, email=instance.email,)
    return dict(
        access_token=create_access_token(data),
        token_type="bearer",
    )
