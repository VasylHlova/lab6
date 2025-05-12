from typing import Optional, List
from sqlmodel import Session, select
from app.models.users import User, UserCreate, UserUpdate
from app.crud.base import CRUDBase

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        result = db.exec(statement).first()
        return result

    def get_active(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        statement = select(User).where(User.is_active == True).offset(skip).limit(limit)
        return db.exec(statement).all()

crud_users = CRUDUser(User)