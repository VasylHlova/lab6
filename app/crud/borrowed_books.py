from typing import Optional, List
from sqlmodel import Session, select
from app.models.borrowed_books import BorrowedBook, BorrowedBookCreate, BorrowedBookUpdate
from app.crud.base import CRUDBase

class CRUDBorrowedBook(CRUDBase[BorrowedBook, BorrowedBookCreate, BorrowedBookUpdate]):
    def get_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[BorrowedBook]:
        statement = select(BorrowedBook).where(BorrowedBook.user_id == user_id).offset(skip).limit(limit)
        return db.exec(statement).all()
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        book_id: Optional[int] = None
    ) -> List[BorrowedBook]:
        statement = select(BorrowedBook)
        if user_id is not None:
            statement = statement.where(BorrowedBook.user_id == user_id)
        if book_id is not None:
            statement = statement.where(BorrowedBook.book_id == book_id)
        statement = statement.offset(skip).limit(limit)
        return db.exec(statement).all()
    
    def return_book(self, db: Session, borrowed_id: int) -> Optional[BorrowedBook]:
        borrowed = db.get(BorrowedBook, borrowed_id)
        if borrowed:
            from datetime import datetime, timezone
            borrowed.real_return_date = datetime.now(timezone.utc)
            db.add(borrowed)
            db.commit()
            db.refresh(borrowed)
        return borrowed

crud_borrowed = CRUDBorrowedBook(BorrowedBook)