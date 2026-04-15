from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from datetime import datetime
from .database import Base

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
