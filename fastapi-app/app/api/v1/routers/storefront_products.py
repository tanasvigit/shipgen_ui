"""
Storefront product endpoints (/storefront/v1/products).
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.storefront_product import StorefrontProduct
from app.schemas.storefront import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/storefront/v1/products", tags=["storefront-products"])


@router.get("/", response_model=List[ProductOut])
def list_products(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    store_uuid: Optional[str] = Query(None),
    category_uuid: Optional[str] = Query(None),
    is_available: Optional[bool] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    """List products."""
    query = db.query(StorefrontProduct).filter(StorefrontProduct.deleted_at.is_(None))
    
    if store_uuid:
        query = query.filter(StorefrontProduct.store_uuid == store_uuid)
    if category_uuid:
        query = query.filter(StorefrontProduct.category_uuid == category_uuid)
    if is_available is not None:
        query = query.filter(StorefrontProduct.is_available == is_available)
    if status:
        query = query.filter(StorefrontProduct.status == status)
    if search:
        query = query.filter(
            (StorefrontProduct.name.ilike(f"%{search}%")) |
            (StorefrontProduct.description.ilike(f"%{search}%"))
        )
    
    products = query.offset(offset).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: str,
    db: Session = Depends(get_db),
):
    """Get a product by public_id or uuid."""
    product = db.query(StorefrontProduct).filter(
        (StorefrontProduct.public_id == product_id) | (StorefrontProduct.uuid == product_id),
        StorefrontProduct.deleted_at.is_(None)
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    
    return product


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
):
    """Create a new product."""
    product_uuid = str(uuid.uuid4())
    public_id = f"product_{uuid.uuid4().hex[:12]}"
    
    # Generate slug from name
    slug = payload.name.lower().replace(" ", "-") if payload.name else None
    
    product = StorefrontProduct(
        uuid=product_uuid,
        public_id=public_id,
        name=payload.name,
        description=payload.description,
        tags=payload.tags or [],
        sku=payload.sku,
        price=payload.price,
        sale_price=payload.sale_price,
        currency=payload.currency or "USD",
        is_service=payload.is_service,
        is_bookable=payload.is_bookable,
        is_available=payload.is_available,
        is_on_sale=payload.is_on_sale,
        is_recommended=payload.is_recommended,
        can_pickup=payload.can_pickup,
        status=payload.status or "available",
        meta=payload.meta,
        youtube_urls=payload.youtube_urls or [],
        store_uuid=payload.store_uuid,
        category_uuid=payload.category_uuid,
        primary_image_uuid=payload.primary_image_uuid,
        slug=slug,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: str,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
):
    """Update a product."""
    product = db.query(StorefrontProduct).filter(
        (StorefrontProduct.public_id == product_id) | (StorefrontProduct.uuid == product_id),
        StorefrontProduct.deleted_at.is_(None)
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    # Update slug if name changed
    if "name" in update_data and product.name:
        product.slug = product.name.lower().replace(" ", "-")
    
    product.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(product)
    
    return product

