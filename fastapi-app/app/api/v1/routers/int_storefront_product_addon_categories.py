from typing import List, Optional, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_product_addon_category import StorefrontProductAddonCategory
from app.models.user import User

router = APIRouter(prefix="/int/v1/product-addon-categories", tags=["int-storefront-product-addon-categories"])


class ProductAddonCategoryCreate(BaseModel):
    product_uuid: str
    category_uuid: Optional[str] = None
    excluded_addons: Optional[list[str]] = None
    max_selectable: Optional[int] = None
    is_required: bool = False


class ProductAddonCategoryUpdate(BaseModel):
    product_uuid: Optional[str] = None
    category_uuid: Optional[str] = None
    excluded_addons: Optional[list[str]] = None
    max_selectable: Optional[int] = None
    is_required: Optional[bool] = None


@router.get("/", response_model=List[dict])
def list_product_addon_categories(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    categories = db.query(StorefrontProductAddonCategory).filter(
        StorefrontProductAddonCategory.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [cat.__dict__ for cat in categories]


@router.get("/{id}", response_model=dict)
def get_product_addon_category(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    category = db.query(StorefrontProductAddonCategory).filter(
        (StorefrontProductAddonCategory.uuid == id) | (StorefrontProductAddonCategory.id == int(id) if id.isdigit() else False),
        StorefrontProductAddonCategory.deleted_at.is_(None)
    ).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product addon category not found")
    return category.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_product_addon_category(
    payload: ProductAddonCategoryCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    category = StorefrontProductAddonCategory()
    category.uuid = str(uuid.uuid4())
    category.product_uuid = payload.product_uuid
    category.category_uuid = payload.category_uuid
    category.excluded_addons = payload.excluded_addons
    category.max_selectable = payload.max_selectable
    category.is_required = payload.is_required
    
    db.add(category)
    db.commit()
    db.refresh(category)
    return category.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_product_addon_category(
    id: str,
    payload: ProductAddonCategoryUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    category = db.query(StorefrontProductAddonCategory).filter(
        (StorefrontProductAddonCategory.uuid == id) | (StorefrontProductAddonCategory.id == int(id) if id.isdigit() else False),
        StorefrontProductAddonCategory.deleted_at.is_(None)
    ).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product addon category not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(category, field):
            setattr(category, field, value)
    
    db.add(category)
    db.commit()
    db.refresh(category)
    return category.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_product_addon_category(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    category = db.query(StorefrontProductAddonCategory).filter(
        (StorefrontProductAddonCategory.uuid == id) | (StorefrontProductAddonCategory.id == int(id) if id.isdigit() else False),
        StorefrontProductAddonCategory.deleted_at.is_(None)
    ).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product addon category not found")
    
    category.deleted_at = datetime.utcnow()
    db.add(category)
    db.commit()
    return category.__dict__

