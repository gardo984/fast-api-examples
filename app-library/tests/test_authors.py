import pytest
from typing import List
from faker import Faker
from fastapi import status
from app.db.models import Author


class TestAuthors:

    @pytest.fixture()
    def load_authors(self, db_session) -> List[Author]:
        fake = Faker()
        items_to_create = [
            Author(
                name=fake.name(),
                email=fake.email(),
                age=fake.random_int(min=20,max=100),
                active=True,
            )
            for _ in range(10)
        ]
        db_session.add_all(items_to_create)
        db_session.commit()
        for instance in items_to_create:
            db_session.refresh(instance)
        return items_to_create

    @pytest.mark.parametrize(
        "payload, status_code", [
            (dict(
                name="Author test", active=True,
                age=20, email="test@test.com",
            ), status.HTTP_201_CREATED),
            (dict(name=None, active=False), status.HTTP_422_UNPROCESSABLE_CONTENT),
        ])
    def test_author_create(
        self, client, db_session, payload, status_code,
    ):
        client._authenticate()
        response = client.post("/author/", json=payload)
        outcome = response.json()
        assert response.status_code == status_code

    def test_author_list(self, client, db_session, load_authors):
        client._authenticate()
        response = client.get("/author/")
        authors = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(authors, list)
        assert len(authors) > 0

    def test_author_by_id(self, client, db_session, load_authors):
        client._authenticate()
        response = client.get("/author/")
        authors = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(authors) > 0

        for item in authors:
            author_id = item.get('id')
            response = client.get(f"/author/{author_id}/")
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["id"] == author_id

    def test_author_update(self, client, db_session, load_authors):
        author = load_authors[0]
        client._authenticate()
        new_name = f"{author.name}_test"
        payload = dict(
            name=new_name,
            age=20,
            email="test1@test.com",
            active=(not author.active),
        )
        response = client.put(
            f"/author/{author.id}/", json=payload,
        )
        outcome = response.json()

        author = db_session.query(Author).where(
            Author.id == author.id
        ).first()
        assert author is not None
        assert response.status_code == status.HTTP_200_OK
        assert author.active is False and author.name == new_name

    def test_author_delete(self, client, db_session, load_authors):
        author = load_authors[0]
        author_id = author.id
        client._authenticate()
        response = client.delete(f"/author/{author_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        author = db_session.query(Author).where(
            Author.id == author_id
        ).first()
        assert author is None

        response = client.delete(f"/author/{author_id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
