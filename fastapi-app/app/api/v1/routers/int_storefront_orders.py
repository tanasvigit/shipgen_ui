from typing import Any, Optional
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.order import Order
from app.models.user import User
from app.utils.order_helpers import patch_order_config, create_order_activity, assign_driver_to_order

class OrderCreate(BaseModel):
    customer_uuid: Optional[str] = None
    customer_type: Optional[str] = "contact"
    type: str = "storefront"
    internal_id: Optional[str] = None
    notes: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    meta: Optional[dict[str, Any]] = None
    options: Optional[dict[str, Any]] = None
    status: Optional[str] = "pending"

class OrderUpdate(BaseModel):
    internal_id: Optional[str] = None
    notes: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    options: Optional[dict[str, Any]] = None
    driver_assigned_uuid: Optional[str] = None

class MarkReadyRequest(BaseModel):
    adhoc: bool = False
    driver: Optional[str] = None

router = APIRouter(prefix="/int/v1/orders", tags=["int-storefront-orders"])


@router.get("/", response_model=list)
def list_orders(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    orders = db.query(Order).filter(
        Order.company_uuid == current.company_uuid,
        Order.type == "storefront",
        Order.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [order.__dict__ for order in orders]


@router.get("/{id}", response_model=dict)
def get_order(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    order = db.query(Order).filter(
        Order.company_uuid == current.company_uuid,
        (Order.uuid == id) | (Order.public_id == id),
        Order.deleted_at.is_(None)
    ).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Create a new storefront order."""
    order_uuid = str(uuid.uuid4())
    order = Order(
        uuid=order_uuid,
        public_id=f"order_{uuid.uuid4().hex[:12]}",
        company_uuid=current.company_uuid,
        customer_uuid=payload.customer_uuid,
        customer_type=payload.customer_type or "contact",
        type=payload.type or "storefront",
        internal_id=payload.internal_id,
        notes=payload.notes,
        scheduled_at=payload.scheduled_at,
        meta=payload.meta or {},
        options=payload.options or {},
        status=payload.status or "pending",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    db.add(order)
    db.flush()
    
    # Create activity log
    create_order_activity(
        db,
        order,
        "created",
        f"Order {order.public_id} created",
        causer_uuid=current.uuid,
        causer_type="user"
    )
    
    db.commit()
    db.refresh(order)
    
    return order.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_order(
    id: str,
    payload: OrderUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Update an order."""
    order = db.query(Order).filter(
        Order.company_uuid == current.company_uuid,
        (Order.uuid == id) | (Order.public_id == id),
        Order.deleted_at.is_(None)
    ).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    old_status = order.status
    
    # Update fields
    update_data = payload.dict(exclude_unset=True)
    
    # Handle meta/options updates
    if "meta" in update_data or "options" in update_data:
        patch_order_config(order, {
            "meta": update_data.get("meta"),
            "options": update_data.get("options")
        })
        update_data.pop("meta", None)
        update_data.pop("options", None)
    
    # Handle driver assignment
    if "driver_assigned_uuid" in update_data:
        driver_uuid = update_data.pop("driver_assigned_uuid")
        if driver_uuid:
            if not assign_driver_to_order(db, order, driver_uuid):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid driver UUID"
                )
    
    # Update other fields
    for field, value in update_data.items():
        if hasattr(order, field):
            setattr(order, field, value)
    
    order.updated_at = datetime.now(timezone.utc)
    
    # Create activity log if status changed
    if "status" in update_data and old_status != order.status:
        create_order_activity(
            db,
            order,
            "updated",
            f"Order status changed from {old_status} to {order.status}",
            causer_uuid=current.uuid,
            causer_type="user",
            properties={"old_status": old_status, "new_status": order.status}
        )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    return order.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_order(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    order = db.query(Order).filter(
        Order.company_uuid == current.company_uuid,
        (Order.uuid == id) | (Order.public_id == id),
        Order.deleted_at.is_(None)
    ).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    from datetime import datetime
    order.deleted_at = datetime.utcnow()
    db.add(order)
    db.commit()
    return order.__dict__


@router.post("/{id}/accept", response_model=dict)
def accept_order(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Accept an order."""
    order = db.query(Order).filter(
        Order.company_uuid == current.company_uuid,
        (Order.uuid == id) | (Order.public_id == id),
        Order.deleted_at.is_(None)
    ).first()
    
    if not order:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No order to accept!")
    
    # Update order config
    patch_order_config(order, {
        "meta": {"accepted_at": datetime.now(timezone.utc).isoformat()},
        "options": {"accepted_by": current.uuid}
    })
    
    order.status = "accepted"
    order.updated_at = datetime.now(timezone.utc)
    
    # Create activity
    create_order_activity(
        db,
        order,
        "accepted",
        f"Order {order.public_id} accepted",
        causer_uuid=current.uuid,
        causer_type="user"
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return {
        "status": "ok",
        "order": order.public_id,
        "status": order.status,
    }


@router.post("/{id}/ready", response_model=dict)
def mark_order_as_ready(
    id: str,
    payload: Optional[MarkReadyRequest] = None,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Mark order as ready."""
    adhoc = payload.adhoc if payload else False
    driver = payload.driver if payload else None
    
    order = db.query(Order).filter(
        Order.company_uuid == current.company_uuid,
        (Order.uuid == id) | (Order.public_id == id),
        Order.deleted_at.is_(None)
    ).first()
    
    if not order:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No order to update!")
    
    # Handle pickup vs delivery
    is_pickup = order.meta and order.meta.get("is_pickup", False)
    
    if is_pickup:
        order.status = "pickup_ready"
        patch_order_config(order, {
            "meta": {"ready_at": datetime.now(timezone.utc).isoformat()}
        })
    else:
        # Delivery order
        if adhoc:
            order.adhoc = True
        
        # Assign driver if provided
        if driver:
            if not assign_driver_to_order(db, order, driver):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid driver UUID"
                )
        
        order.status = "dispatched"
        order.dispatched = True
        order.dispatched_at = datetime.now(timezone.utc)
        
        patch_order_config(order, {
            "meta": {"ready_at": datetime.now(timezone.utc).isoformat()}
        })
    
    # Create activity
    create_order_activity(
        db,
        order,
        "ready",
        f"Order {order.public_id} marked as ready",
        causer_uuid=current.uuid,
        causer_type="user"
    )
    
    order.updated_at = datetime.now(timezone.utc)
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return {
        "status": "ok",
        "order": order.public_id,
        "status": order.status,
    }


@router.post("/{id}/preparing", response_model=dict)
def mark_order_as_preparing(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Mark order as preparing."""
    order = db.query(Order).filter(
        Order.company_uuid == current.company_uuid,
        (Order.uuid == id) | (Order.public_id == id),
        Order.deleted_at.is_(None)
    ).first()
    
    if not order:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No order to update!")
    
    # Update order config
    patch_order_config(order, {
        "meta": {"preparing_at": datetime.now(timezone.utc).isoformat()}
    })
    
    order.status = "preparing"
    order.updated_at = datetime.now(timezone.utc)
    
    # Create activity
    create_order_activity(
        db,
        order,
        "preparing",
        f"Order {order.public_id} is being prepared",
        causer_uuid=current.uuid,
        causer_type="user"
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return {
        "status": "ok",
        "order": order.public_id,
        "status": order.status,
    }


@router.post("/{id}/completed", response_model=dict)
def mark_order_as_completed(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Mark order as completed."""
    order = db.query(Order).filter(
        Order.company_uuid == current.company_uuid,
        (Order.uuid == id) | (Order.public_id == id),
        Order.deleted_at.is_(None)
    ).first()
    
    if not order:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No order to update!")
    
    # Update order config
    patch_order_config(order, {
        "meta": {"completed_at": datetime.now(timezone.utc).isoformat()},
        "options": {"completed_by": current.uuid}
    })
    
    order.status = "completed"
    order.updated_at = datetime.now(timezone.utc)
    
    # Create activity
    create_order_activity(
        db,
        order,
        "completed",
        f"Order {order.public_id} completed",
        causer_uuid=current.uuid,
        causer_type="user"
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return {
        "status": "ok",
        "order": order.public_id,
        "status": order.status,
    }

