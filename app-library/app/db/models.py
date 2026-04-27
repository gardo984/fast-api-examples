from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from datetime import datetime
from sqlalchemy.orm import Session
from .database import Base
from typing import Union, List, Tuple, Any, Optional
from ..utils import hash_password, verify_password_hash


class BaseStructure(Base):
    __abstract__ = True
    id = Column(Integer, nullable=False, primary_key=True,)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=text("now()"),
        nullable=True,
    )
    created_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        default=None,
    )


class User(BaseStructure):
    __tablename__ = "users"
    email = Column(String(60), nullable=False,)
    password = Column(String(120), nullable=False,)
    disabled = Column(Boolean, default=False, nullable=False,)

    # relationships
    created_by = relationship(
        "User",
        back_populates="users",
        remote_side="User.id",
        foreign_keys="User.created_by_id",
    )
    users = relationship("User", back_populates="created_by")
    authors = relationship("Author", back_populates="created_by")
    categories = relationship("Category", back_populates="created_by")
    books = relationship("Book", back_populates="created_by")
    purchases = relationship("Purchase", back_populates="created_by")
    # likes = relationship("Likes", back_populates="user")

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
    def create_users(
        cls, db: Session,
        users: List,
        current_user: Optional[Any] = None,
    ) -> List:
        users_to_create: List[cls] = []
        for user_data in users:
            user_data.password = cls.get_password_hash(user_data.password)
            payload = user_data.dict()
            if current_user:
                payload.update({"created_by_id": current_user.id})
            db_user = cls(**payload)
            db.add(db_user)
            users_to_create.append(db_user)

        db.commit()
        for user in users_to_create:
            db.refresh(user)

        if len(users_to_create) > 1:
            return users_to_create
        else:
            return users_to_create[0]


class Author(BaseStructure):
    __tablename__ = "authors"
    name = Column(String(100), nullable=False)
    email = Column(String(50), nullable=False)
    age = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, server_default=text("TRUE"))

    # relationships
    created_by = relationship("User", back_populates="authors")
    books = relationship("Book", back_populates="author")

    @classmethod
    def validate_existence(
        cls, instance_id: int, db: Session,
    ) -> "Optional[Author]":
        instance = db.query(cls).where(cls.id == instance_id).first()
        return instance


class Category(BaseStructure):
    __tablename__ = "categories"
    name = Column(String(100), nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    # relationships
    created_by = relationship("User", back_populates="categories")
    books = relationship("Book", back_populates="category")

    @classmethod
    def validate_existence(
        cls, instance_id: int, db: Session,
    ) -> "Optional[Category]":
        instance = db.query(cls).where(cls.id == instance_id).first()
        return instance


class Book(BaseStructure):
    __tablename__ = "books"
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    # relationships
    created_by = relationship("User", back_populates="books")
    author = relationship("Author", back_populates="books")
    category = relationship("Category", back_populates="books")
    purchases = relationship("Purchase", back_populates="book")
    # likes = relationship("Likes", back_populates="book")


class Purchase(BaseStructure):
    __tablename__ = "purchases"
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    # relationships
    created_by = relationship("User", back_populates="purchases")
    book = relationship("Book", back_populates="purchases")


# class Likes(BaseStructure):
#     __tablename__ = "likes"

#     book_id = Column(Integer, ForeignKey("books.id"),
#                      nullable=False, primary_key=True, )
#     user_id = Column(Integer, ForeignKey("users.id"),
#                      nullable=False, primary_key=True, )

#     # relationships
#     user = relationship("User", back_populates="likes")
#     book = relationship("Book", back_populates="likes")
