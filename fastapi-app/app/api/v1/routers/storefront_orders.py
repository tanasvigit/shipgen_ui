"""
Storefront order endpoints (/storefront/v1/orders).
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.order import Order
from app.models.contact import Contact
from app.utils.storefront_auth import get_storefront_customer, require_storefront_customer

router = APIRouter(prefix="/storefront/v1/orders", tags=["storefront-orders"])


@router.put("/picked-up", status_code=status.HTTP_200_OK)
def complete_order_pickup(
    order: str,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """Mark a pickup order as completed by customer."""
    customer = require_storefront_customer(db, authorization)
    
    order_obj = db.query(Order).filter(
        Order.public_id == order,
        Order.deleted_at.is_(None)
    ).first()
    
    if not order_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )
    
    # Verify customer owns this order
    if order_obj.customer_uuid != customer.uuid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized.")
    
    # Update order status
    order_obj.status = "completed"
    db.commit()
    db.refresh(order_obj)
    
    return {
        "status": "ok",
        "order": order_obj.public_id,
        "order_status": order_obj.status,
    }


@router.post("/receipt", response_model=dict)
def get_order_receipt(
    order: str,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """Get receipt for an order."""
    customer = require_storefront_customer(db, authorization)
    
    order_obj = db.query(Order).filter(
        Order.public_id == order,
        Order.deleted_at.is_(None)
    ).first()
    
    if not order_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )
    
    # Verify customer owns this order
    if order_obj.customer_uuid != customer.uuid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized.")
    
    # Return basic receipt data
    return {
        "order_id": order_obj.public_id,
        "status": order_obj.status,
        "message": "Receipt data would be generated based on payment method",
    }

