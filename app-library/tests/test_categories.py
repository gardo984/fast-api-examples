import pytest
from typing import List
from faker import Faker
from fastapi import status
from app.db.models import Category


class TestCategories:

    @pytest.fixture()
    def load_categories(self, db_session) -> List[Category]:
        fake = Faker()
        items_to_create = [
            Category(name=fake.name(), active=True)
            for _ in range(10)
        ]
        db_session.add_all(items_to_create)
        db_session.commit()
        for instance in items_to_create:
            db_session.refresh(instance)
        return items_to_create

    @pytest.mark.parametrize(
        "payload, status_code", [
            (dict(name="Category test", active=True), status.HTTP_201_CREATED),
            (dict(name=None, active=False), status.HTTP_422_UNPROCESSABLE_CONTENT),
        ])
    def test_category_create(
        self, client, db_session, payload, status_code,
    ):
        client._authenticate()
        response = client.post("/categories/", json=payload)
        outcome = response.json()
        assert response.status_code == status_code

    def test_category_list(self, client, db_session, load_categories):
        client._authenticate()
        response = client.get("/categories/")
        categories = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(categories, list)
        assert len(categories) > 0

    def test_category_by_id(self, client, db_session, load_categories):
        client._authenticate()
        response = client.get("/categories/")
        categories = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(categories) > 0

        for item in categories:
            category_id = item.get('id')
            response = client.get(f"/categories/{category_id}/")
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["id"] == category_id

    def test_category_update(self, client, db_session, load_categories):
        category = load_categories[0]
        client._authenticate()
        new_name = f"{category.name}_test"
        payload = dict(name=new_name, active=(not category.active))
        response = client.put(
            f"/categories/{category.id}/", json=payload,
        )
        outcome = response.json()

        category = db_session.query(Category).where(
            Category.id == category.id
        ).first()
        assert category is not None
        assert response.status_code == status.HTTP_200_OK
        assert category.active is False and category.name == new_name

    def test_category_delete(self, client, db_session, load_categories):
        category = load_categories[0]
        category_id = category.id
        client._authenticate()
        response = client.delete(f"/categories/{category_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        category = db_session.query(Category).where(
            Category.id == category_id
        ).first()
        assert category is None

        response = client.delete(f"/categories/{category_id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
