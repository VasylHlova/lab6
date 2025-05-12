from typing import Optional
from sqlmodel import Session, select
from app.models.categories import Category, CategoryCreate, CategoryUpdate
from app.crud.base import CRUDBase

class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def get_by_name(self, db: Session, name: str) -> Optional[Category]:
        statement = select(Category).where(Category.name == name)
        return db.exec(statement).first()

crud_categories = CRUDCategory(Category)