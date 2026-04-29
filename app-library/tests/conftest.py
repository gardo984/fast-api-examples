
import pytest
import json
from typing import Dict, Any
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.config import settings
from app.db.database import get_db, Base
from app.db.models import User
from app.schemas import UserCreate
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

database_test = f"{settings.database_name}_test"
db_connection = f"mysql+pymysql://{settings.database_user}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{database_test}"  # noqa

user_credentials = dict(
    email="admin@admin.com",
    password="12345678",
)


@pytest.fixture(scope="session")
def engine():
    db_engine = f"mysql+pymysql://{settings.database_user}:{settings.database_password}@{settings.database_host}:{settings.database_port}"  # noqa
    default_engine = create_engine(db_engine)
    with default_engine.connect() as connection:
        connection.execute(text(f"drop database if exists {database_test};"))
        connection.execute(text(f"create database {database_test};"))

    test_engine = create_engine(db_connection)
    yield test_engine

    # clean up
    Base.metadata.drop_all(bind=test_engine)
    with default_engine.connect() as connection:
        connection.execute(text(f"drop database if exists {database_test};"))


@pytest.fixture(scope="function")
def db_session(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine)
    db = TestSessionLocal()
    yield db
    db.close()


class AuthenticatedClient(TestClient):

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.access_token = None

    def _authenticate(self):
        outcome = self.login(*user_credentials.values())
        assert outcome is not None
        assert isinstance(outcome, Dict)
        assert "access_token" in outcome

    def login(self, username: str, password: str) -> Dict[str, Any]:
        payload = dict(email=username, password=password)
        response = self.post("/login/", json=payload)
        if response.status_code == status.HTTP_200_OK:
            self.access_token = response.json().get("access_token")
            self.headers.update({
                "Authorization": f"Bearer {self.access_token}"
            })
        return response.json()

    def request(self, method, *args, **kwargs):
        if self.access_token and "headers" in kwargs:
            if kwargs["headers"]:
                kwargs["headers"].update(self.headers)
            else:
                kwargs["headers"] = self.headers
        elif self.access_token and "headers" not in kwargs:
            kwargs["headers"] = self.headers
        return super().request(method, *args, **kwargs)


@pytest.fixture()
def super_user(db_session: Session) -> User:
    user_data = UserCreate(**user_credentials)
    outcome = User.create_users(db=db_session, users=[user_data])
    assert outcome is not None
    assert isinstance(outcome, User)
    return outcome


@pytest.fixture(scope="function")
def client(db_session: Session, super_user: User):
    def _get_test_session():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = _get_test_session
    with AuthenticatedClient() as test_client:
        yield test_client
