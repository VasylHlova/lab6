from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.db.database import get_session
from app.models.users import UserCreate, UserRead, UserUpdate
from app.crud.users import crud_users

router = APIRouter()

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
        user: UserCreate,
        db: Session = Depends(get_session)
):
    return crud_users.create(db=db, obj_in=user)

@router.get("/", response_model=List[UserRead])
def read_users(
        *,
        db: Session = Depends(get_session),
        skip: int = 0,
        limit: int = 100
):
    return crud_users.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserRead)
def read_user(
        *,
        user_id: int,
        db: Session = Depends(get_session)
):
    user = crud_users.get(db=db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user

@router.get("/email/{email}", response_model=UserRead)
def read_user_by_email(
        *,
        email: str,
        db: Session = Depends(get_session)
):
    user = crud_users.get_by_email(db=db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found"
        )
    return user

@router.get("/active", response_model=List[UserRead])
def read_active_users(
        *,
        db: Session = Depends(get_session),
        skip: int = 0,
        limit: int = 100
):
    return crud_users.get_active(db=db, skip=skip, limit=limit)

@router.put("/{user_id}", response_model=UserRead)
def update_user(
        *,
        user_id: int,
        user: UserUpdate,
        db: Session = Depends(get_session)
):
    db_user = crud_users.get(db=db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    return crud_users.update(db=db, db_obj=db_user, obj_in=user)

@router.delete("/{user_id}", response_model=UserRead)
def delete_user(
        *,
        user_id: int,
        db: Session = Depends(get_session)
):
    user = crud_users.get(db=db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    # Перевірка на наявність BorrowedBook
    if user.borrowed_books:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has borrowed books and cannot be deleted, please return them first"
        )
    return crud_users.remove(db=db, id=user_id)