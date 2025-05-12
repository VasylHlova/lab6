from fastapi import APIRouter, Depends
from sqlmodel import Session,func
from app.db.database import get_session
from app.models.books import Book, BookAuthorLink, BookCategoryLink
from app.models.borrowed_books import BorrowedBook 
from app.models.authors import Author
from app.models.categories import Category 

router = APIRouter()

@router.get("/popular-books")
def get_popular_books(limit: int = 5, session: Session = Depends(get_session)):
    result = (
        session.query(Book, func.count(BorrowedBook.id).label("borrow_count"))
        .join(BorrowedBook, BorrowedBook.book_id == Book.id)
        .group_by(Book.id)
        .order_by(func.count(BorrowedBook.id).desc())
        .limit(limit)
        .all()
    )
    return [
        {"book": book.title, "borrow_count": borrow_count}
        for book, borrow_count in result
    ]

@router.get("/popular-authors")
def get_popular_authors(limit: int = 5, session: Session = Depends(get_session)):
    result = (
        session.query(Author, func.count(BorrowedBook.id).label("borrow_count"))
        .join(BookAuthorLink, BookAuthorLink.author_id == Author.id)
        .join(BorrowedBook, BorrowedBook.book_id == BookAuthorLink.book_id)
        .group_by(Author.id)
        .order_by(func.count(BorrowedBook.id).desc())
        .limit(limit)
        .all()
    )
    return [
        {"author": f"{author.first_name} {author.last_name}", "borrow_count": borrow_count}
        for author, borrow_count in result
    ]

@router.get("/popular-categories")
def get_popular_categories(limit: int = 5, session: Session = Depends(get_session)):
    result = (
        session.query(Category, func.count(BorrowedBook.id).label("borrow_count"))
        .join(BookCategoryLink, BookCategoryLink.category_id == Category.id)
        .join(BorrowedBook, BorrowedBook.book_id == BookCategoryLink.book_id)
        .group_by(Category.id)
        .order_by(func.count(BorrowedBook.id).desc())
        .limit(limit)
        .all()
    )
    return [
        {"category": category.name, "borrow_count": borrow_count}
        for category, borrow_count in result
    ]