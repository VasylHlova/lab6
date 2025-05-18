from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.categories import Category
from app.db.database import get_session
from app.models.categories import CategoryCreate, CategoryRead, CategoryUpdate
from app.crud.categories import crud_categories

router = APIRouter()

@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
        category: CategoryCreate,
        db: Session = Depends(get_session)
):
    existing = db.exec(select(Category).where(Category.name == category.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    return crud_categories.create(db=db, obj_in=category)

@router.get("/", response_model=List[CategoryRead])
def read_categories(
        *,
        db: Session = Depends(get_session),
        skip: int = 0,
        limit: int = 100
):
    return crud_categories.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{category_id}", response_model=CategoryRead)
def read_category(
        *,
        category_id: int,
        db: Session = Depends(get_session)
):
    category = crud_categories.get(db=db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    return category

@router.get("/name/{name}", response_model=CategoryRead)
def read_category_by_name(
        *,
        name: str,
        db: Session = Depends(get_session)
):
    category = crud_categories.get_by_name(db=db, name=name)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with name {name} not found"
        )
    return category

@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_session)
):
    if category.name is not None and not category.name.strip():
        raise HTTPException(status_code=400, detail="Category name cannot be empty")
    db_category = crud_categories.get(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud_categories.update(db=db, db_obj=db_category, obj_in=category)

@router.delete("/{category_id}", response_model=CategoryRead)
def delete_category(
        *,
        category_id: int,
        db: Session = Depends(get_session)
):
    category = crud_categories.get(db=db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )

    if category.books:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category with ID {category_id} because it has associated books"
        )
    return crud_categories.remove(db=db, id=category_id)