from typing import List, Optional, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.category import Category
from app.models.user import User

router = APIRouter(prefix="/int/v1/addon-categories", tags=["int-storefront-addon-categories"])


class AddonCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    for_type: str = "storefront_product_addon"


class AddonCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


@router.get("/", response_model=List[dict])
def list_addon_categories(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    categories = db.query(Category).filter(
        Category.company_uuid == current.company_uuid,
        Category.for_type == "storefront_product_addon",
        Category.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [cat.__dict__ for cat in categories]


@router.get("/{id}", response_model=dict)
def get_addon_category(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    category = db.query(Category).filter(
        Category.company_uuid == current.company_uuid,
        Category.for_type == "storefront_product_addon",
        (Category.uuid == id) | (Category.public_id == id),
        Category.deleted_at.is_(None)
    ).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Addon category not found")
    return category.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_addon_category(
    payload: AddonCategoryCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    category = Category()
    category.uuid = str(uuid.uuid4())
    category.company_uuid = current.company_uuid
    category.created_by_uuid = current.uuid
    category.name = payload.name
    category.description = payload.description
    category.for_type = payload.for_type
    
    db.add(category)
    db.commit()
    db.refresh(category)
    return category.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_addon_category(
    id: str,
    payload: AddonCategoryUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    category = db.query(Category).filter(
        Category.company_uuid == current.company_uuid,
        Category.for_type == "storefront_product_addon",
        (Category.uuid == id) | (Category.public_id == id),
        Category.deleted_at.is_(None)
    ).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Addon category not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(category, field):
            setattr(category, field, value)
    
    db.add(category)
    db.commit()
    db.refresh(category)
    return category.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_addon_category(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    category = db.query(Category).filter(
        Category.company_uuid == current.company_uuid,
        Category.for_type == "storefront_product_addon",
        (Category.uuid == id) | (Category.public_id == id),
        Category.deleted_at.is_(None)
    ).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Addon category not found")
    
    category.deleted_at = datetime.utcnow()
    db.add(category)
    db.commit()
    return category.__dict__

