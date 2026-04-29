import pytest
from fastapi import status
from typing import List
from faker import Faker
from app.db.models import Author, Category


class AppFixtures:

    @pytest.fixture()
    def load_categories(self, db_session) -> List[int]:
        fake = Faker()
        items_to_create = [
            Category(name=fake.name(), active=True)
            for _ in range(10)
        ]
        db_session.add_all(items_to_create)
        db_session.commit()
        for instance in items_to_create:
            db_session.refresh(instance)
        return [x.id for x in items_to_create]

    @pytest.fixture()
    def load_authors(self, db_session) -> List[int]:
        fake = Faker()
        items_to_create = [
            Author(
                name=fake.name(),
                email=fake.email(),
                age=fake.random_int(min=20, max=100),
                active=True,
            )
            for _ in range(10)
        ]
        db_session.add_all(items_to_create)
        db_session.commit()
        for instance in items_to_create:
            db_session.refresh(instance)
        return [x.id for x in items_to_create]


class TestMain:

    @pytest.mark.parametrize(
        "method, status_code", [
            ("get", status.HTTP_200_OK),
            ("post", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("delete", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("head", status.HTTP_405_METHOD_NOT_ALLOWED),
        ])
    def test_main_endpoint(
        self, client, method, status_code,
    ):
        method = getattr(client, method)
        response = method("/")
        assert response.status_code == status_code
