from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    birth_date: Mapped[str] = mapped_column(String, nullable=False)
    year_of_death: Mapped[str] = mapped_column(String, nullable=True)

    def __repr__(self)->str:
        return f"Task {self.id}"


class Book(db.Model):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("authors.id"), nullable=False)
    isbn: Mapped[str] = mapped_column(String(255), nullable=False)
    publication_year: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self)->str:
        return f"Task {self.id}"



