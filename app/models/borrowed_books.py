from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.users import User
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone



class BorrowedBookBase(SQLModel):
    borrowed_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    return_date: Optional[datetime] = Field(default=None)
    real_return_date: Optional[datetime] = Field(default=None)

class BorrowedBook(BorrowedBookBase, table=True):
    __tablename__ = "borrowed_book"

    id: Optional[int] = Field(default=None, primary_key=True)
    user: "User" = Relationship(back_populates="borrowed_books")
    user_id: int = Field(foreign_key="user.id")
    book_id: int = Field(foreign_key="book.id", ondelete="CASCADE")
        
class BorrowedBookCreate(BorrowedBookBase):
    return_date: Optional[datetime] = None
    user_id: int
    book_id: int    
    
class BorrowedBookUpdate(SQLModel):
    borrowed_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    user_id: Optional[int] = None
    book_id: Optional[int] = None    

class BorrowedBookRead(BorrowedBookBase):
    id: int
    user_id: int
    book_id: int
    borrowed_date: datetime
    return_date: Optional[datetime] = None
    real_return_date: Optional[datetime] = None

    class Config:
        form_attributes = True   