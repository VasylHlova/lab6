from app.models.authors import Author, AuthorCreate, AuthorUpdate
from app.crud.base import CRUDBase
from datetime import datetime, timezone


class CRUDAuthor(CRUDBase[Author, AuthorCreate, AuthorUpdate]):
    def update(self, db, *, db_obj, obj_in):
        update_data = obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            setattr(db_obj, field, update_data[field])

        db_obj.updated_at = datetime.now(timezone.utc)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj


crud_authors = CRUDAuthor(Author)
