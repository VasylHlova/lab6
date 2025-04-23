from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.database import get_session
from app.models.authors import AuthorCreate, AuthorRead, AuthorUpdate
from app.crud.authors import crud_authors

router = APIRouter()


@router.post("/", response_model=AuthorRead, status_code=status.HTTP_201_CREATED)
def create_author(
        author: AuthorCreate,
        db: Session = Depends(get_session)
):
    return crud_authors.create(db=db, obj_in=author)


@router.get("/", response_model=List[AuthorRead])
def read_authors(
        *,
        db: Session = Depends(get_session),
        skip: int = 0,
        limit: int = 100
):
    return crud_authors.get_multi(db=db, skip=skip, limit=limit)


@router.get("/{author_id}", response_model=AuthorRead)
def read_author(
        *,
        author_id: int,
        db: Session = Depends(get_session)
):
    author = crud_authors.get(db=db, id=author_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with ID {author_id} not found"
        )
    return author


@router.put("/{author_id}", response_model=AuthorRead)
def update_author(
        *,
        author_id: int,
        author: AuthorUpdate,
        db: Session = Depends(get_session)
):
    db_author = crud_authors.get(db=db, id=author_id)
    if not db_author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with ID {author_id} not found"
        )

    return crud_authors.update(db=db, db_obj=db_author, obj_in=author)


@router.delete("/{author_id}", response_model=AuthorRead)
def delete_author(
        *,
        author_id: int,
        db: Session = Depends(get_session)
):
    author = crud_authors.get(db=db, id=author_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with ID {author_id} not found"
        )

    # Check if author has books
    if author.books:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete author with ID {author_id} because they have associated books"
        )

    return crud_authors.remove(db=db, id=author_id)
