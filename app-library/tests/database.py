
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.db.database import get_db, Base
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

database_test = f"{settings.database_name}_test"
db_connection = f"mysql+pymysql://{settings.database_user}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{database_test}"  # noqa


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



@pytest.fixture
def db_session(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine)
    db = TestSessionLocal()
    yield db
    db.close()


@pytest.fixture
def client(db_session: Session):
    def _get_test_session():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = _get_test_session
    test_client = TestClient(app)
    yield test_client
