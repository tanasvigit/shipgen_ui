from datetime import datetime
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut, OrderUpdate, OrderResponse, OrdersResponse

router = APIRouter(prefix="/fleetops/v1/orders", tags=["fleetops-orders"])


@router.get("/", response_model=OrdersResponse)
def list_orders(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
):
    query = db.query(Order).filter(
        Order.deleted_at.is_(None),
        Order.company_uuid == current.company_uuid,
    )
    if status_filter:
        query = query.filter(Order.status == status_filter)
    if search:
        q = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Order.internal_id.ilike(q),
                Order.public_id.ilike(q),
                Order.uuid.ilike(q),
                Order.notes.ilike(q),
                Order.type.ilike(q),
            )
        )

    def _parse_iso(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            # Accept both `...Z` and offset formats.
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None

    start_dt = _parse_iso(start_date)
    end_dt = _parse_iso(end_date)
    if start_dt:
        query = query.filter(Order.created_at.is_not(None), Order.created_at >= start_dt)
    if end_dt:
        query = query.filter(Order.created_at.is_not(None), Order.created_at <= end_dt)

    orders = query.offset(offset).limit(limit).all()
    return {"orders": orders}


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    order = db.query(Order).filter((Order.uuid == order_id) | (Order.public_id == order_id)).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    return {"order": order}


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Create a new order with generated UUIDs
    order = Order(
        uuid=str(uuid.uuid4()),
        public_id=f"order_{uuid.uuid4().hex[:12]}",
        type=payload.type,
        internal_id=payload.internal_id,
        notes=payload.notes,
        scheduled_at=payload.scheduled_at,
        meta=payload.meta,
        options=payload.options,
        company_uuid=current.company_uuid,
        status="created",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return {"order": order}


@router.put("/{order_id}", response_model=OrderResponse)
@router.patch("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: str,
    payload: OrderUpdate,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    order = db.query(Order).filter((Order.uuid == order_id) | (Order.public_id == order_id)).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    for field, value in payload.dict(exclude_unset=True).items():
        if field == "created_at":
            continue
        setattr(order, field, value)
    order.updated_at = datetime.utcnow()

    db.add(order)
    db.commit()
    db.refresh(order)

    return {"order": order}


@router.delete("/{order_id}", response_model=OrderResponse)
def delete_order(
    order_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    order = db.query(Order).filter((Order.uuid == order_id) | (Order.public_id == order_id)).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    order.deleted_at = datetime.utcnow()
    db.add(order)
    db.commit()
    return {"order": order}


@router.delete("/{order_id}/delete", response_model=OrderResponse)
def delete_order_by_path(
    order_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """DELETE /orders/{order_id}/delete – same soft-delete as DELETE /orders/{order_id} (spec path)."""
    return delete_order(order_id, db, _current)


@router.post("/{order_id}/start", response_model=OrderResponse)
def start_order(
    order_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    order = db.query(Order).filter((Order.uuid == order_id) | (Order.public_id == order_id)).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    order.started = True
    order.started_at = datetime.utcnow()
    order.status = "in_progress"
    db.add(order)
    db.commit()
    db.refresh(order)
    return {"order": order}


@router.post("/{order_id}/complete", response_model=OrderResponse)
def complete_order(
    order_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    order = db.query(Order).filter((Order.uuid == order_id) | (Order.public_id == order_id)).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    order.status = "completed"
    db.add(order)
    db.commit()
    db.refresh(order)
    return {"order": order}


@router.delete("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    order = db.query(Order).filter((Order.uuid == order_id) | (Order.public_id == order_id)).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    order.status = "cancelled"
    db.add(order)
    db.commit()
    db.refresh(order)
    return {"order": order}


@router.post("/{order_id}/schedule", response_model=OrderResponse)
@router.patch("/{order_id}/schedule", response_model=OrderResponse)
def schedule_order(
    order_id: str,
    scheduled_at: datetime | None = None,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Set or update the scheduled_at time and status for an order."""
    order = db.query(Order).filter((Order.uuid == order_id) | (Order.public_id == order_id)).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    if scheduled_at is None:
        scheduled_at = datetime.utcnow()

    order.scheduled_at = scheduled_at
    # Preserve explicit status if already progressed; otherwise mark scheduled
    if not order.status or order.status in {"created", "scheduled"}:
        order.status = "scheduled"

    db.add(order)
    db.commit()
    db.refresh(order)
    return {"order": order}


@router.post("/{order_id}/dispatch", response_model=OrderResponse)
@router.patch("/{order_id}/dispatch", response_model=OrderResponse)
def dispatch_order(
    order_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Mark an order as dispatched."""
    order = db.query(Order).filter((Order.uuid == order_id) | (Order.public_id == order_id)).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    order.dispatched = True
    order.dispatched_at = datetime.utcnow()
    if order.status not in {"in_progress", "completed", "cancelled"}:
        order.status = "dispatched"

    db.add(order)
    db.commit()
    db.refresh(order)
    return {"order": order}


@router.get("/{order_id}/distance-and-time")
def get_distance_and_time(
    order_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Return stored distance and time fields for an order."""
    order = db.query(Order).filter((Order.uuid == order_id) | (Order.public_id == order_id)).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    return {"distance": order.distance, "time": order.time}


@router.get("/{order_id}/eta")
def get_eta(
    order_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Simple ETA estimation using stored time value."""
    order = db.query(Order).filter((Order.uuid == order_id) | (Order.public_id == order_id)).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    return {
        "order_uuid": order.uuid,
        "status": order.status,
        "eta_seconds": order.time,
    }


@router.get("/{order_id}/tracker")
def tracker_data(
    order_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Return a minimal tracker payload for the order."""
    order = db.query(Order).filter((Order.uuid == order_id) | (Order.public_id == order_id)).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    return {
        "order_uuid": order.uuid,
        "status": order.status,
        "started": order.started,
        "started_at": order.started_at,
        "dispatched": order.dispatched,
        "dispatched_at": order.dispatched_at,
        "scheduled_at": order.scheduled_at,
        "driver_assigned_uuid": order.driver_assigned_uuid,
    }


@router.get("/{order_id}/distance-and-time")
def get_distance_and_time(
    order_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Return stored distance and time fields for an order."""
    order = db.query(Order).filter(Order.uuid == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    return {"distance": order.distance, "time": order.time}


@router.get("/{order_id}/eta")
def get_eta(
    order_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Simple ETA estimation using stored time value."""
    order = db.query(Order).filter(Order.uuid == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    return {
        "order_uuid": order.uuid,
        "status": order.status,
        "eta_seconds": order.time,
    }


@router.get("/{order_id}/tracker")
def tracker_data(
    order_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Return a minimal tracker payload for the order."""
    order = db.query(Order).filter(Order.uuid == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    return {
        "order_uuid": order.uuid,
        "status": order.status,
        "started": order.started,
        "started_at": order.started_at,
        "dispatched": order.dispatched,
        "dispatched_at": order.dispatched_at,
        "scheduled_at": order.scheduled_at,
        "driver_assigned_uuid": order.driver_assigned_uuid,
    }



