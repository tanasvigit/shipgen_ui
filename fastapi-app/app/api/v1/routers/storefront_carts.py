"""
Storefront cart endpoints (/storefront/v1/carts).
"""
import uuid
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.storefront_product import StorefrontProduct
from app.models.storefront_cart import StorefrontCart
from app.schemas.storefront import CartOut, AddToCartRequest, UpdateCartItemRequest

router = APIRouter(prefix="/storefront/v1/carts", tags=["storefront-carts"])


def _retrieve_cart(cart_id: Optional[str], db: Session, exclude_checkedout: bool = True) -> StorefrontCart:
    """Retrieve or create a cart."""
    if cart_id:
        query = db.query(StorefrontCart).filter(
            (StorefrontCart.public_id == cart_id) |
            (StorefrontCart.unique_identifier == cart_id),
            StorefrontCart.deleted_at.is_(None)
        )
        if exclude_checkedout:
            query = query.filter(StorefrontCart.checkout_uuid.is_(None))
        
        cart = query.first()
        if cart:
            return cart
    
    # Create new cart
    cart_uuid = str(uuid.uuid4())
    public_id = f"cart_{uuid.uuid4().hex[:12]}"
    unique_id = cart_id if cart_id and not cart_id.startswith("cart_") else None
    
    cart = StorefrontCart(
        uuid=cart_uuid,
        public_id=public_id,
        unique_identifier=unique_id,
        items=[],
        events=[],
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    db.add(cart)
    db.commit()
    db.refresh(cart)
    
    return cart


def _calculate_product_subtotal(product: StorefrontProduct, quantity: int, variants: list, addons: list) -> int:
    """Calculate subtotal for a product with variants and addons."""
    price = product.sale_price if product.is_on_sale else product.price
    subtotal = price
    
    # Add variant costs
    for variant in variants or []:
        additional_cost = variant.get("additional_cost", 0)
        if isinstance(additional_cost, str):
            additional_cost = int("".join(filter(str.isdigit, additional_cost)))
        subtotal += additional_cost
    
    # Add addon costs
    for addon in addons or []:
        addon_price = addon.get("sale_price") if addon.get("is_on_sale") else addon.get("price", 0)
        if isinstance(addon_price, str):
            addon_price = int("".join(filter(str.isdigit, addon_price)))
        subtotal += addon_price
    
    return subtotal * quantity


@router.get("/", response_model=CartOut)
@router.get("/{cart_id}", response_model=CartOut)
def retrieve_cart(
    cart_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Retrieve or create a cart."""
    cart = _retrieve_cart(cart_id, db)
    
    # Add computed fields
    cart.subtotal = cart.calculate_subtotal()
    cart.total_items = cart.get_total_items()
    cart.total_unique_items = cart.get_total_unique_items()
    
    return cart


@router.post("/{cart_id}/{product_id}", response_model=CartOut)
def add_to_cart(
    cart_id: str,
    product_id: str,
    payload: AddToCartRequest,
    db: Session = Depends(get_db),
):
    """Add a product to cart."""
    cart = _retrieve_cart(cart_id, db)
    
    if cart.checkout_uuid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart has already been checked out."
        )
    
    # Find product
    product = db.query(StorefrontProduct).filter(
        (StorefrontProduct.public_id == product_id) | (StorefrontProduct.uuid == product_id),
        StorefrontProduct.deleted_at.is_(None),
        StorefrontProduct.is_available == True
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or unavailable."
        )
    
    # Calculate subtotal
    subtotal = _calculate_product_subtotal(
        product,
        payload.quantity,
        payload.variants or [],
        payload.addons or []
    )
    
    # Get price
    price = product.sale_price if product.is_on_sale else product.price
    
    # Create cart item
    item_id = f"cart_item_{uuid.uuid4().hex[:12]}"
    cart_item = {
        "id": item_id,
        "store_id": product.store_uuid or "",
        "store_location_id": payload.store_location,
        "product_id": product.public_id,
        "product_image_url": None,  # Would be populated from product.primary_image
        "name": product.name,
        "description": product.description,
        "quantity": payload.quantity,
        "price": price,
        "subtotal": subtotal,
        "variants": payload.variants or [],
        "addons": payload.addons or [],
        "scheduled_at": payload.scheduled_at,
        "created_at": int(time.time()),
        "updated_at": int(time.time()),
        "meta": product.meta or {},
    }
    
    # Add item to cart
    items = cart.items or []
    items.append(cart_item)
    cart.items = items
    
    # Update currency
    if product.currency:
        cart.currency = product.currency
    
    # Add event
    events = cart.events or []
    events.append({
        "event": "cart.item_added",
        "cart_item_id": item_id,
        "time": int(time.time()),
    })
    cart.events = events
    
    cart.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cart)
    
    cart.subtotal = cart.calculate_subtotal()
    cart.total_items = cart.get_total_items()
    cart.total_unique_items = cart.get_total_unique_items()
    
    return cart


@router.put("/{cart_id}/{line_item_id}", response_model=CartOut)
def update_cart_item(
    cart_id: str,
    line_item_id: str,
    payload: UpdateCartItemRequest,
    db: Session = Depends(get_db),
):
    """Update a line item in the cart."""
    cart = _retrieve_cart(cart_id, db)
    
    if cart.checkout_uuid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart has already been checked out."
        )
    
    items = cart.items or []
    item_index = None
    for i, item in enumerate(items):
        if item.get("id") == line_item_id:
            item_index = i
            break
    
    if item_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found."
        )
    
    # Get product to recalculate
    item = items[item_index]
    product = db.query(StorefrontProduct).filter(
        StorefrontProduct.public_id == item.get("product_id"),
        StorefrontProduct.deleted_at.is_(None)
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    
    # Update item
    quantity = payload.quantity if payload.quantity is not None else item.get("quantity", 1)
    variants = payload.variants if payload.variants is not None else item.get("variants", [])
    addons = payload.addons if payload.addons is not None else item.get("addons", [])
    
    subtotal = _calculate_product_subtotal(product, quantity, variants, addons)
    price = product.sale_price if product.is_on_sale else product.price
    
    items[item_index].update({
        "quantity": quantity,
        "variants": variants,
        "addons": addons,
        "price": price,
        "subtotal": subtotal,
        "scheduled_at": payload.scheduled_at or item.get("scheduled_at"),
        "updated_at": int(time.time()),
    })
    
    cart.items = items
    
    # Add event
    events = cart.events or []
    events.append({
        "event": "cart.item_updated",
        "cart_item_id": line_item_id,
        "time": int(time.time()),
    })
    cart.events = events
    
    cart.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cart)
    
    cart.subtotal = cart.calculate_subtotal()
    cart.total_items = cart.get_total_items()
    cart.total_unique_items = cart.get_total_unique_items()
    
    return cart


@router.delete("/{cart_id}/{line_item_id}", response_model=CartOut)
def remove_cart_item(
    cart_id: str,
    line_item_id: str,
    db: Session = Depends(get_db),
):
    """Remove a line item from the cart."""
    cart = _retrieve_cart(cart_id, db)
    
    if cart.checkout_uuid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart has already been checked out."
        )
    
    items = cart.items or []
    item_index = None
    for i, item in enumerate(items):
        if item.get("id") == line_item_id:
            item_index = i
            break
    
    if item_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found."
        )
    
    # Remove item
    items.pop(item_index)
    cart.items = items
    
    # Add event
    events = cart.events or []
    events.append({
        "event": "cart.item_removed",
        "cart_item_id": line_item_id,
        "time": int(time.time()),
    })
    cart.events = events
    
    cart.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cart)
    
    cart.subtotal = cart.calculate_subtotal()
    cart.total_items = cart.get_total_items()
    cart.total_unique_items = cart.get_total_unique_items()
    
    return cart


@router.put("/{cart_id}/empty", response_model=CartOut)
def empty_cart(
    cart_id: str,
    db: Session = Depends(get_db),
):
    """Empty the cart."""
    cart = _retrieve_cart(cart_id, db)
    
    cart.items = []
    cart.currency = None
    
    # Add event
    events = cart.events or []
    events.append({
        "event": "cart.emptied",
        "cart_item_id": None,
        "time": int(time.time()),
    })
    cart.events = events
    
    cart.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cart)
    
    cart.subtotal = cart.calculate_subtotal()
    cart.total_items = cart.get_total_items()
    cart.total_unique_items = cart.get_total_unique_items()
    
    return cart


@router.delete("/{cart_id}", status_code=status.HTTP_200_OK)
def delete_cart(
    cart_id: str,
    db: Session = Depends(get_db),
):
    """Delete a cart."""
    cart = db.query(StorefrontCart).filter(
        (StorefrontCart.public_id == cart_id) | (StorefrontCart.unique_identifier == cart_id),
        StorefrontCart.deleted_at.is_(None)
    ).first()
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found."
        )
    
    cart.deleted_at = datetime.now(timezone.utc)
    db.commit()
    
    return {"message": "Cart deleted successfully."}

