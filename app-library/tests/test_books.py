import pytest
from typing import List
from faker import Faker
from fastapi import status
from app.db.models import Author, Category, Book
from tests.test_main import AppFixtures


class TestBooks(AppFixtures):

    @pytest.fixture()
    def load_books(self, db_session, load_categories, load_authors) -> List[int]:
        fake = Faker()
        items_to_create = [
            Book(
                name=fake.name(),
                category_id=fake.random_element(load_categories),
                author_id=fake.random_element(load_authors),
                active=True,
            )
            for _ in range(10)
        ]
        db_session.add_all(items_to_create)
        db_session.commit()
        for instance in items_to_create:
            db_session.refresh(instance)
        return [x.id for x in items_to_create]

    def test_book_create(
        self, client, db_session, load_categories, load_authors
    ):
        category = db_session.query(Category).where(
            Category.id == load_categories[0]
        ).first()
        author = db_session.query(Author).where(
            Author.id == load_authors[0]
        ).first()
        assert category is not None
        assert author is not None

        client._authenticate()
        payload = dict(
            name="The last penguin", category_id=category.id,
            author_id=author.id, active=True,
        )
        response = client.post("/books/", json=payload)
        outcome = response.json()
        assert response.status_code == status.HTTP_201_CREATED

    def test_book_list(self, client, db_session, load_books):
        print(load_books)
        client._authenticate()
        response = client.get("/books/")
        books = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(books, list)
        assert len(books) > 0

    def test_book_by_id(self, client, db_session, load_books):
        client._authenticate()
        response = client.get("/books/")
        books = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(books) > 0

        for item in books:
            book_id = item.get('id')
            response = client.get(f"/books/{book_id}/")
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["id"] == book_id

    def test_book_update(self, client, db_session, load_books):
        book = db_session.query(Book).where(
            Book.id == load_books[0]
        ).first()
        assert book is not None

        client._authenticate()
        new_name = f"{book.name}_test"
        payload = dict(
            name=new_name,
            category_id=book.category_id,
            author_id=book.author_id,
            active=(not book.active),
        )
        response = client.put(
            f"/books/{book.id}/", json=payload,
        )
        outcome = response.json()

        book = db_session.query(Book).where(
            Book.id == book.id
        ).first()
        assert book is not None
        assert response.status_code == status.HTTP_200_OK
        assert book.active is False and book.name == new_name

    def test_book_delete(self, client, db_session, load_books):
        book = db_session.query(Book).where(
            Book.id == load_books[0]
        ).first()
        assert book is not None

        book_id = book.id
        client._authenticate()
        response = client.delete(f"/books/{book_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        book = db_session.query(Book).where(
            Book.id == book_id
        ).first()
        assert book is None

        response = client.delete(f"/books/{book_id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
