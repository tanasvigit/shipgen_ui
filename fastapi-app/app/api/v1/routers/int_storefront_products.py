from typing import List, Optional, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_product import StorefrontProduct
from app.models.entity import Entity
from app.models.user import User

router = APIRouter(prefix="/int/v1/products", tags=["int-storefront-products"])


class ProductCreate(BaseModel):
    store_uuid: Optional[str] = None
    category_uuid: Optional[str] = None
    name: str
    description: Optional[str] = None
    price: int = 0
    sale_price: int = 0
    currency: Optional[str] = None


class ProductUpdate(BaseModel):
    store_uuid: Optional[str] = None
    category_uuid: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    sale_price: Optional[int] = None
    currency: Optional[str] = None


class ProcessImportsRequest(BaseModel):
    imports: List[dict[str, Any]]


class CreateEntitiesRequest(BaseModel):
    entities: List[dict[str, Any]]


@router.get("/", response_model=List[dict])
def list_products(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    products = db.query(StorefrontProduct).filter(
        StorefrontProduct.company_uuid == current.company_uuid,
        StorefrontProduct.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [p.__dict__ for p in products]


@router.get("/{id}", response_model=dict)
def get_product(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    product = db.query(StorefrontProduct).filter(
        StorefrontProduct.company_uuid == current.company_uuid,
        (StorefrontProduct.uuid == id) | (StorefrontProduct.public_id == id),
        StorefrontProduct.deleted_at.is_(None)
    ).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    product = StorefrontProduct()
    product.uuid = str(uuid.uuid4())
    product.company_uuid = current.company_uuid
    product.created_by_uuid = current.uuid
    product.store_uuid = payload.store_uuid
    product.category_uuid = payload.category_uuid
    product.name = payload.name
    product.description = payload.description
    product.price = payload.price
    product.sale_price = payload.sale_price
    product.currency = payload.currency
    
    db.add(product)
    db.commit()
    db.refresh(product)
    return product.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_product(
    id: str,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    product = db.query(StorefrontProduct).filter(
        StorefrontProduct.company_uuid == current.company_uuid,
        (StorefrontProduct.uuid == id) | (StorefrontProduct.public_id == id),
        StorefrontProduct.deleted_at.is_(None)
    ).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(product, field):
            setattr(product, field, value)
    
    db.add(product)
    db.commit()
    db.refresh(product)
    return product.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_product(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    product = db.query(StorefrontProduct).filter(
        StorefrontProduct.company_uuid == current.company_uuid,
        (StorefrontProduct.uuid == id) | (StorefrontProduct.public_id == id),
        StorefrontProduct.deleted_at.is_(None)
    ).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    product.deleted_at = datetime.utcnow()
    db.add(product)
    db.commit()
    return product.__dict__


@router.post("/process-imports", response_model=dict)
def process_imports(
    payload: ProcessImportsRequest,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Process product imports from CSV/Excel data."""
    from app.models.storefront_product import StorefrontProduct
    from datetime import datetime, timezone
    
    processed = 0
    errors = []
    created_products = []
    
    for import_item in payload.imports:
        try:
            # Extract product data from import item
            product_data = import_item if isinstance(import_item, dict) else import_item.dict()
            
            # Validate required fields
            if not product_data.get("name"):
                errors.append({"item": import_item, "error": "Product name is required"})
                continue
            
            # Check if product already exists (by SKU or name)
            existing = None
            if product_data.get("sku"):
                existing = db.query(StorefrontProduct).filter(
                    StorefrontProduct.company_uuid == current.company_uuid,
                    StorefrontProduct.sku == product_data["sku"],
                    StorefrontProduct.deleted_at.is_(None)
                ).first()
            
            if existing:
                # Update existing product
                for key, value in product_data.items():
                    if hasattr(existing, key) and key not in ["uuid", "public_id", "created_at"]:
                        setattr(existing, key, value)
                existing.updated_at = datetime.now(timezone.utc)
                db.add(existing)
            else:
                # Create new product
                product = StorefrontProduct()
                product.uuid = str(uuid.uuid4())
                product.public_id = f"prod_{uuid.uuid4().hex[:12]}"
                product.company_uuid = current.company_uuid
                product.created_by_uuid = current.uuid
                product.name = product_data.get("name")
                product.description = product_data.get("description")
                product.sku = product_data.get("sku")
                product.price = int(float(product_data.get("price", 0)) * 100)  # Convert to cents
                product.sale_price = int(float(product_data.get("sale_price", 0)) * 100) if product_data.get("sale_price") else None
                product.currency = product_data.get("currency", "USD")
                product.is_on_sale = product_data.get("is_on_sale", False)
                product.is_available = product_data.get("is_available", True)
                product.status = product_data.get("status", "available")
                product.store_uuid = product_data.get("store_uuid")
                product.category_uuid = product_data.get("category_uuid")
                product.meta = product_data.get("meta", {})
                product.created_at = datetime.now(timezone.utc)
                product.updated_at = datetime.now(timezone.utc)
                
                db.add(product)
                created_products.append(product.public_id)
            
            processed += 1
        except Exception as e:
            errors.append({"item": import_item, "error": str(e)})
    
    db.commit()
    
    return {
        "status": "ok",
        "processed": processed,
        "created": len(created_products),
        "created_products": created_products,
        "errors": errors,
    }


@router.post("/create-entities", response_model=dict)
def create_entities(
    payload: CreateEntitiesRequest,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Create entity records linked to products."""
    from datetime import datetime, timezone
    
    created = []
    errors = []
    
    for entity_data in payload.entities:
        try:
            entity = Entity()
            entity.uuid = str(uuid.uuid4())
            entity.public_id = f"entity_{uuid.uuid4().hex[:12]}"
            entity.company_uuid = current.company_uuid
            entity.created_by_uuid = current.uuid
            entity.name = entity_data.get("name")
            entity.type = entity_data.get("type", "product")
            entity.internal_id = entity_data.get("internal_id")
            entity.meta = entity_data.get("meta", {})
            
            # Link to product if product_uuid provided
            if entity_data.get("product_uuid"):
                entity.meta = entity.meta or {}
                entity.meta["product_uuid"] = entity_data["product_uuid"]
            
            entity.created_at = datetime.now(timezone.utc)
            entity.updated_at = datetime.now(timezone.utc)
            
            db.add(entity)
            db.flush()
            created.append(entity.public_id)
        except Exception as e:
            errors.append({"entity": entity_data, "error": str(e)})
    
    db.commit()
    
    return {
        "status": "ok",
        "created": len(created),
        "entities": created,
        "errors": errors,
    }

