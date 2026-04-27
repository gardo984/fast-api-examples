
import typer
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import (
    User, Category, Author, Book,
)
from app.schemas import UserCreate
from faker import Faker

app = typer.Typer()
fake = Faker()


@app.command()
def create_superuser(
    email: str = "admin@admin.com",
    password: str = "0e542d2231",
    db_session=None,
):
    """Create an admin user"""
    db = SessionLocal() if not db_session else db_session
    users = [UserCreate(email=email, password=password),]
    instance = User.create_users(db, users)
    typer.echo(f"Superuser {email} created!")


def _load_random_users():
    """ Generate random users """
    db = SessionLocal()
    current_user = db.query(User).first()
    if not current_user:
        # in case there is not super admin, create one
        create_superuser(db_session=db)
        current_user = db.query(User).first()

    items_to_create: List[User] = []
    for item in range(20):
        hashed_password = User.get_password_hash(
            ''.join(fake.random_letters()))
        db_user = User(
            email=fake.email(),
            password=hashed_password,
            created_by_id=current_user.id,
        )
        items_to_create.append(db_user)

    db.add_all(items_to_create)
    db.commit()
    typer.echo(f"Users were created: {len(items_to_create)} items")


def _load_categories():
    """ Generate random categories """
    db = SessionLocal()
    items_to_create = []
    for item in range(20):
        current_user = fake.random_element(db.query(User).all())
        db_category = Category(name=fake.job_male(),
                               created_by_id=current_user.id,)
        items_to_create.append(db_category)

    db.add_all(items_to_create)
    db.commit()
    typer.echo(f"Categories were created: {len(items_to_create)} items")


def _load_authors():
    """ Generate random authors """
    db = SessionLocal()
    items_to_create = []
    for item in range(20):
        current_user = fake.random_element(db.query(User).all())
        db_author = Author(
            name=fake.name(),
            email=fake.email(),
            age=fake.random_int(min=18, max=100),
            active=True,
            created_by_id=current_user.id,
        )
        items_to_create.append(db_author)

    db.add_all(items_to_create)
    db.commit()
    typer.echo(f"Authors were created: {len(items_to_create)} items")


def _load_books():
    """ Generate random books bound to category and author. """
    db = SessionLocal()
    items_to_create: List[Book] = []
    for item in range(20):
        current_user = fake.random_element(db.query(User).all())
        category = fake.random_element(db.query(Category).all())
        author = fake.random_element(db.query(Author).all())
        db_book = Book(
            name=fake.name(),
            category_id=category.id,
            author_id=author.id,
            active=True,
            created_by_id=current_user.id,
        )
        items_to_create.append(db_book)

    db.add_all(items_to_create)
    db.commit()
    typer.echo(f"Books were created: {len(items_to_create)} items")


@app.command()
def load_dev_data():
    _load_random_users()
    _load_categories()
    _load_authors()
    _load_books()


if __name__ == "__main__":
    app()
