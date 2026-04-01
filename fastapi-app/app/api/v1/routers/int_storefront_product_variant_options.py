from typing import List, Optional, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_product_variant_option import StorefrontProductVariantOption
from app.models.user import User

router = APIRouter(prefix="/int/v1/product-variant-options", tags=["int-storefront-product-variant-options"])


class ProductVariantOptionCreate(BaseModel):
    product_variant_uuid: str
    name: str
    description: Optional[str] = None
    translations: Optional[dict[str, Any]] = None
    meta: Optional[dict[str, Any]] = None
    additional_cost: int = 0


class ProductVariantOptionUpdate(BaseModel):
    product_variant_uuid: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    translations: Optional[dict[str, Any]] = None
    meta: Optional[dict[str, Any]] = None
    additional_cost: Optional[int] = None


@router.get("/", response_model=List[dict])
def list_product_variant_options(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    options = db.query(StorefrontProductVariantOption).filter(
        StorefrontProductVariantOption.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [opt.__dict__ for opt in options]


@router.get("/{id}", response_model=dict)
def get_product_variant_option(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    option = db.query(StorefrontProductVariantOption).filter(
        (StorefrontProductVariantOption.uuid == id) | (StorefrontProductVariantOption.public_id == id),
        StorefrontProductVariantOption.deleted_at.is_(None)
    ).first()
    if not option:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product variant option not found")
    return option.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_product_variant_option(
    payload: ProductVariantOptionCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    option = StorefrontProductVariantOption()
    option.uuid = str(uuid.uuid4())
    option.product_variant_uuid = payload.product_variant_uuid
    option.name = payload.name
    option.description = payload.description
    option.translations = payload.translations
    option.meta = payload.meta
    option.additional_cost = payload.additional_cost
    
    db.add(option)
    db.commit()
    db.refresh(option)
    return option.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_product_variant_option(
    id: str,
    payload: ProductVariantOptionUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    option = db.query(StorefrontProductVariantOption).filter(
        (StorefrontProductVariantOption.uuid == id) | (StorefrontProductVariantOption.public_id == id),
        StorefrontProductVariantOption.deleted_at.is_(None)
    ).first()
    if not option:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product variant option not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(option, field):
            setattr(option, field, value)
    
    db.add(option)
    db.commit()
    db.refresh(option)
    return option.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_product_variant_option(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    option = db.query(StorefrontProductVariantOption).filter(
        (StorefrontProductVariantOption.uuid == id) | (StorefrontProductVariantOption.public_id == id),
        StorefrontProductVariantOption.deleted_at.is_(None)
    ).first()
    if not option:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product variant option not found")
    
    option.deleted_at = datetime.utcnow()
    db.add(option)
    db.commit()
    return option.__dict__

