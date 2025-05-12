# app/models/books.py
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from app.models.authors import Author
    from app.models.categories import Category
    from app.models.borrowed_books import BorrowedBook

from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone


class BookAuthorLink(SQLModel, table=True):
    __tablename__ = "book_author_link"

    book_id: Optional[int] = Field(
        default=None, foreign_key="book.id", primary_key=True
    )
    author_id: Optional[int] = Field(
        default=None, foreign_key="author.id", primary_key=True
    )


class BookCategoryLink(SQLModel, table=True):
    __tablename__ = "book_category_link"

    book_id: Optional[int] = Field(
        default=None, foreign_key="book.id", primary_key=True
    )
    category_id: Optional[int] = Field(
        default=None, foreign_key="category.id", primary_key=True
    )


class BookBase(SQLModel):
    title: str = Field(index=True)
    publication_year: int = Field(default=None)
    isbn: str = Field(unique=True, index=True)
    quantity: int = Field(default=1)


class Book(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    authors: List["Author"] = Relationship(
        back_populates="books",
        link_model=BookAuthorLink
    )
    categories: List["Category"] = Relationship(
        back_populates="books",
        link_model=BookCategoryLink
    )


class BookCreate(BookBase):
    author_ids: List[int] = Field(default_factory=list)
    category_ids: List[int] = Field(default_factory=list)


class BookUpdate(SQLModel):
    title: Optional[str] = None
    publication_year: Optional[int] = None
    isbn: Optional[str] = None
    quantity: Optional[int] = None
    author_ids: List[int] = Field(default_factory=list)
    category_ids: List[int] = Field(default_factory=list)


class BookRead(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        form_attributes = True
        
        
class BookService:
    def has_active_borrows(self, db, book_id: int) -> bool:
        from app.models.borrowed_books import BorrowedBook  # Додайте цей імпорт!
        from sqlmodel import select
        statement = select(BorrowedBook).where(
            (BorrowedBook.book_id == book_id) &
            (BorrowedBook.real_return_date == None)
        )
        return db.exec(statement).first() is not None

    def get_available_copies(self, db, book_id: int) -> int:
        from app.models.borrowed_books import BorrowedBook  # Додайте цей імпорт!
        from app.models.books import Book
        if not book_id:
            return 0
        book = db.get(Book, book_id)
        if not book:
            return 0
        from sqlmodel import select
        statement = select(BorrowedBook).where(
            (BorrowedBook.book_id == book_id) &
            (BorrowedBook.real_return_date == None)
        )
        active_borrows = db.exec(statement).all()
        return book.quantity - len(active_borrows)    
