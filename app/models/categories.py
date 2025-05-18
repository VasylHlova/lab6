from typing import Optional, List

from app.models.books import BookCategoryLink, Book
from sqlmodel import Field, SQLModel, Relationship, UniqueConstraint
from datetime import datetime, timezone


class CategoryBase(SQLModel):
    name: str 
    description: Optional[str] = None
    
class Category(CategoryBase, table=True):
    __tablename__ = "category"
    __table_args__ = (UniqueConstraint("name"),)
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    books: List["Book"] = Relationship(back_populates="categories",
                                       link_model=BookCategoryLink)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    
class CategoryRead(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        form_attributes = True        