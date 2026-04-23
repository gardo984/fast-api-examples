from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from datetime import datetime
from sqlalchemy.orm import Session
from .database import Base
from typing import Union, List, Tuple, Any
from ..utils import hash_password, verify_password_hash


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, nullable=False, primary_key=True,)
    email = Column(String(60), nullable=False,)
    password = Column(String(120), nullable=False,)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=text("now()"),
        nullable=True,
    )
    disabled = Column(Boolean, default=False, nullable=False,)

    @classmethod
    def authenticate_user(
        cls, db: Session, email: str, password: str
    ) -> Tuple[Any, bool]:
        user_instance = db.query(cls).where(cls.email == email).first()
        if not user_instance:
            return False
        return (
            user_instance,
            user_instance.verify_password(password=password),
        )

    @classmethod
    def get_password_hash(cls, value: str) -> str:
        return hash_password(value)

    @classmethod
    def validate_users_existence(
        cls, db: Session, user_list: Union[str, List[str]]
    ) -> List[str]:
        if not isinstance(user_list, List):
            user_list = [user_list]

        stmt = db.query(cls.email).where(cls.email.in_(user_list))
        outcome = db.execute(stmt).scalars().all()
        return outcome

    def verify_password(self, password: str) -> str:
        return verify_password_hash(password, self.password)

    @classmethod
    def create_users(cls, db: Session, users: List) -> List:
        users_to_create: List[cls] = []
        for user_data in users:
            user_data.password = cls.get_password_hash(user_data.password)
            db_user = cls(**user_data.dict())
            db.add(db_user)
            users_to_create.append(db_user)

        db.commit()
        for user in users_to_create:
            db.refresh(user)

        if len(users_to_create) > 1:
            return users_to_create
        else:
            return users_to_create[0]


class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=text("now()"),
        nullable=True,
    )
    name = Column(String(100), nullable=False)
    email = Column(String(50), nullable=False)
    age = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, server_default=text("TRUE"))
    books = relationship("Book", back_populates="author")


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    name = Column(String(100), nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    books = relationship("Book", back_populates="category")


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    author = relationship("Author", back_populates="books")
    category = relationship("Category", back_populates="books")
    purchases = relationship("Purchase", back_populates="book")


class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    book = relationship("Book", back_populates="purchases")
