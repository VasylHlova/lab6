from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session
from app.db.database import get_session
from app.models.borrowed_books import BorrowedBookCreate, BorrowedBookRead, BorrowedBookUpdate
from app.crud.borrowed_books import crud_borrowed

router = APIRouter()

@router.post("/", response_model=BorrowedBookRead, status_code=status.HTTP_201_CREATED)
def create_borrowed(
        borrowed: BorrowedBookCreate,
        db: Session = Depends(get_session)
):
    return crud_borrowed.create(db=db, obj_in=borrowed)

@router.get("/", response_model=List[BorrowedBookRead])
def read_borrowed(
        *,
        db: Session = Depends(get_session),
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = Query(None, alias="user_id"),
        book_id: Optional[int] = Query(None, alias="book_id")
):
    return crud_borrowed.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        book_id=book_id
    )
   
@router.get("/{user_id}", response_model=List[BorrowedBookRead])
def read_borrowed_by_user(
        *,
        user_id: int,
        db: Session = Depends(get_session),
        skip: int = 0,
        limit: int = 100
):
    borrowed_books = crud_borrowed.get_by_user(db=db, user_id=user_id, skip=skip, limit=limit)
    if not borrowed_books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No borrowed books found for user with ID {user_id}"
        )
    return borrowed_books

@router.put("/{borrowed_id}", response_model=BorrowedBookRead)
def update_borrowed(
        *,
        borrowed_id: int,
        borrowed: BorrowedBookUpdate,
        db: Session = Depends(get_session)
):
    db_borrowed = crud_borrowed.get(db=db, id=borrowed_id)
    if not db_borrowed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Borrowed record with ID {borrowed_id} not found"
        )
    return crud_borrowed.return_book(db=db, borrowed_id=borrowed_id)


@router.delete("/{borrowed_id}", response_model=BorrowedBookRead)
def delete_borrowed(
        *,
        borrowed_id: int,
        db: Session = Depends(get_session)
):
    db_borrowed = crud_borrowed.get(db=db, id=borrowed_id)
    if not db_borrowed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Borrowed record with ID {borrowed_id} not found"
        )
    return crud_borrowed.remove(db=db, db_obj=db_borrowed)
    