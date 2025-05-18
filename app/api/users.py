from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.users import User
from sqlalchemy.exc import IntegrityError
from app.db.database import get_session
from app.models.users import UserCreate, UserRead, UserUpdate
from app.crud.users import crud_users
from app.auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash
from app.config import get_settings
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()
settings = get_settings()

@router.post("/", response_model=UserRead, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_session)):
    existing = db.exec(select(User).where(User.email == user.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    try:
        hashed_password = get_password_hash(user.password)
        user_data = user.dict(exclude={"password"})
        user_data["hashed_password"] = hashed_password
        return crud_users.create(db=db, obj_in=user_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
@router.post("/login", response_model=dict)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.email}]    

@router.get("/", response_model=List[UserRead])
def read_users(
        *,
        db: Session = Depends(get_session),
        skip: int = 0,
        limit: int = 100
):
    return crud_users.get_multi(db=db, skip=skip, limit=limit)

@router.get("/active", response_model=List[UserRead])
def read_active_users(
        *,
        db: Session = Depends(get_session),
        skip: int = 0,
        limit: int = 100
):
    return crud_users.get_active(db=db, skip=skip, limit=limit)

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