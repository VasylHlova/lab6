from typing import List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from python_labs.lab6.library.app.models.borrowed_books import BorrowedBook
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from pydantic import EmailStr


class UserBase(SQLModel):
    first_name: str
    last_name: str
    email: EmailStr = Field(unique=True, index=True)


class User(UserBase, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    registration_date: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    hashed_password: str

    # Relationships
    borrowed_books: List["BorrowedBook"] = Relationship(
        back_populates="user"
    )


class UserCreate(UserBase):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True
        use_enum_values = True


class UserUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserRead(UserBase):
    id: int
    registration_date: datetime
    is_active: bool

    class Config:
        form_attributes = True
        
class Token(SQLModel):
    access_token: str
    token_type: str
    
class TokenData(SQLModel):
    email: str | None = None
