from datetime import datetime
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.driver import Driver
from app.models.issue import Issue
from app.models.notification import Notification
from app.models.order import Order
from app.models.order_event import OrderEvent
from app.models.vehicle import Vehicle
from app.models.user import User
from app.schemas.order import OrderResponse
from app.schemas.order_flow import (
    AssignOrderRequest,
    CreateExceptionRequest,
    OrderEventOut,
    TransitionOrderRequest,
)

router = APIRouter(prefix="/fleetops/v1/orders", tags=["fleetops-order-flow"])

LIFECYCLE_ORDER = [
    "created",
    "assigned",
    "dispatched",
    "arrived_at_pickup",
    "picked_up",
    "in_transit",
    "out_for_delivery",
    "delivered",
    "completed",
]
TERMINAL_STATUSES = {"cancelled", "failed"}
SPECIAL_STATUSES = {"delayed", "reassigned"}
ASSIGNMENT_REQUIRED_STATUSES = {
    "assigned",
    "dispatched",
    "arrived_at_pickup",
    "picked_up",
    "in_transit",
    "out_for_delivery",
    "delivered",
    "completed",
}


def _event(
    db: Session,
    *,
    order: Order,
    current: User,
    event_type: str,
    from_status: str | None,
    to_status: str | None,
    payload: dict | None = None,
) -> None:
    db.add(
        OrderEvent(
            uuid=str(uuid.uuid4()),
            public_id=f"oe_{uuid.uuid4().hex[:12]}",
            company_uuid=order.company_uuid,
            order_uuid=order.uuid,
            actor_uuid=current.uuid,
            event_type=event_type,
            from_status=from_status,
            to_status=to_status,
            payload=payload or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )


def _get_order(db: Session, current: User, order_id: str) -> Order:
    order = (
        db.query(Order)
        .filter(
            Order.company_uuid == current.company_uuid,
            Order.deleted_at.is_(None),
            (Order.uuid == order_id) | (Order.public_id == order_id),
        )
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    return order


def _validate_transition(from_status: str | None, to_status: str) -> None:
    if to_status in TERMINAL_STATUSES | SPECIAL_STATUSES:
        return
    if to_status not in LIFECYCLE_ORDER:
        raise HTTPException(status_code=400, detail=f"Unsupported status transition target: {to_status}")

    if from_status in TERMINAL_STATUSES:
        raise HTTPException(status_code=409, detail=f"Cannot transition from terminal status: {from_status}")

    if from_status in SPECIAL_STATUSES:
        from_status = "assigned"

    if from_status not in LIFECYCLE_ORDER:
        from_status = "created"

    from_idx = LIFECYCLE_ORDER.index(from_status)
    to_idx = LIFECYCLE_ORDER.index(to_status)
    if to_idx < from_idx:
        raise HTTPException(status_code=409, detail=f"Backward transition not allowed: {from_status} -> {to_status}")


def _pick_driver(db: Session, current: User, req: AssignOrderRequest) -> Driver:
    requested_driver = req.driver_uuid or req.driver_id
    if requested_driver:
        driver = (
            db.query(Driver)
            .filter(
                Driver.company_uuid == current.company_uuid,
                Driver.deleted_at.is_(None),
                (Driver.uuid == requested_driver) | (Driver.public_id == requested_driver),
            )
            .first()
        )
        if not driver:
            raise HTTPException(status_code=404, detail="Requested driver not found.")
        return driver

    driver = (
        db.query(Driver)
        .filter(
            Driver.company_uuid == current.company_uuid,
            Driver.deleted_at.is_(None),
            Driver.status.in_(["active", "available"]),
        )
        .order_by(Driver.online.desc(), Driver.updated_at.desc().nullslast())
        .first()
    )
    if not driver:
        raise HTTPException(status_code=409, detail="No available driver found for auto assignment.")
    return driver


def _pick_vehicle(db: Session, current: User, req: AssignOrderRequest, driver: Driver, order_uuid: str) -> Vehicle:
    requested_vehicle = req.vehicle_uuid or req.vehicle_id or driver.vehicle_uuid
    if not requested_vehicle:
        raise HTTPException(status_code=400, detail="Vehicle is required for assignment.")

    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.company_uuid == current.company_uuid,
            Vehicle.deleted_at.is_(None),
            (Vehicle.uuid == requested_vehicle) | (Vehicle.public_id == requested_vehicle),
        )
        .first()
    )
    if not vehicle:
        raise HTTPException(status_code=404, detail="Requested vehicle not found.")

    if (vehicle.status or "").lower() != "active":
        raise HTTPException(status_code=409, detail="Vehicle is inactive and cannot be assigned.")

    # When driver already has a mapped vehicle, enforce valid pair.
    if driver.vehicle_uuid and driver.vehicle_uuid != vehicle.uuid:
        raise HTTPException(status_code=409, detail="Selected vehicle does not match driver assignment.")

    in_use = (
        db.query(Order)
        .filter(
            Order.company_uuid == current.company_uuid,
            Order.deleted_at.is_(None),
            Order.vehicle_assigned_uuid == vehicle.uuid,
            Order.uuid != order_uuid,
            Order.status.notin_(["completed", "cancelled", "failed"]),
        )
        .first()
    )
    if in_use:
        raise HTTPException(status_code=409, detail="Vehicle is already assigned to an active order.")

    return vehicle


@router.post("/{order_id}/assign", response_model=OrderResponse)
def assign_order(
    order_id: str,
    payload: AssignOrderRequest,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    order = _get_order(db, current, order_id)
    from_status = order.status or "created"

    if from_status in TERMINAL_STATUSES:
        raise HTTPException(status_code=409, detail=f"Cannot assign a terminal order: {from_status}")

    driver = _pick_driver(db, current, payload)
    vehicle = _pick_vehicle(db, current, payload, driver, order.uuid)
    order.driver_assigned_uuid = driver.uuid
    order.vehicle_assigned_uuid = vehicle.uuid
    order.status = "assigned"
    order.updated_at = datetime.utcnow()

    _event(
        db,
        order=order,
        current=current,
        event_type="order_assigned",
        from_status=from_status,
        to_status=order.status,
        payload={
            "assignment_mode": payload.mode,
            "driver_uuid": driver.uuid,
            "vehicle_uuid": vehicle.uuid,
            "note": payload.note,
        },
    )

    # Create user-level notification for assigned driver if mapped.
    if driver.user_uuid:
        db.add(
            Notification(
                id=str(uuid.uuid4()),
                type="order.assigned",
                notifiable_type="user",
                notifiable_id=driver.user_uuid,
                data=json.dumps(
                    {
                        "order_uuid": order.uuid,
                        "order_public_id": order.public_id,
                        "message": f"You have been assigned order {order.public_id or order.uuid}.",
                    }
                ),
                read_at=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )

    db.add(order)
    db.commit()
    db.refresh(order)
    return {"order": order}


@router.post("/{order_id}/transition", response_model=OrderResponse)
def transition_order(
    order_id: str,
    payload: TransitionOrderRequest,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    order = _get_order(db, current, order_id)
    from_status = order.status or "created"
    to_status = payload.to_status.strip().lower()
    _validate_transition(from_status, to_status)
    if to_status in ASSIGNMENT_REQUIRED_STATUSES and (
        not order.driver_assigned_uuid or not order.vehicle_assigned_uuid
    ):
        raise HTTPException(
            status_code=400,
            detail="Driver and vehicle must be assigned before progressing the order",
        )

    order.status = to_status
    now = datetime.utcnow()
    if to_status == "dispatched":
        order.dispatched = True
        order.dispatched_at = now
    if to_status in {"in_transit", "picked_up"}:
        order.started = True
        if not order.started_at:
            order.started_at = now
    order.updated_at = now

    _event(
        db,
        order=order,
        current=current,
        event_type="order_status_changed",
        from_status=from_status,
        to_status=to_status,
        payload={"note": payload.note, "meta": payload.meta or {}},
    )

    db.add(order)
    db.commit()
    db.refresh(order)
    return {"order": order}


@router.post("/{order_id}/exceptions", response_model=OrderResponse)
def create_order_exception(
    order_id: str,
    payload: CreateExceptionRequest,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    order = _get_order(db, current, order_id)
    from_status = order.status or "created"

    issue = Issue(
        uuid=str(uuid.uuid4()),
        public_id=f"issue_{uuid.uuid4().hex[:12]}",
        company_uuid=current.company_uuid,
        driver_uuid=order.driver_assigned_uuid,
        reported_by_uuid=current.uuid,
        category=payload.category,
        type=payload.type,
        title=payload.title,
        report=payload.report,
        priority=payload.priority,
        status=payload.status,
        meta={**(payload.meta or {}), "order_uuid": order.uuid, "order_public_id": order.public_id},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(issue)

    if payload.reassign_driver_uuid:
        driver = _pick_driver(db, current, AssignOrderRequest(driver_uuid=payload.reassign_driver_uuid))
        order.driver_assigned_uuid = driver.uuid
        order.status = "reassigned"
        next_status = "reassigned"
    else:
        order.status = "delayed"
        next_status = "delayed"

    order.updated_at = datetime.utcnow()
    _event(
        db,
        order=order,
        current=current,
        event_type="order_exception_raised",
        from_status=from_status,
        to_status=next_status,
        payload={
            "issue_uuid": issue.uuid,
            "issue_public_id": issue.public_id,
            "reassigned_to_driver_uuid": payload.reassign_driver_uuid,
        },
    )

    db.add(order)
    db.commit()
    db.refresh(order)
    return {"order": order}


@router.get("/{order_id}/lifecycle", response_model=list[OrderEventOut])
def get_order_lifecycle(
    order_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    order = _get_order(db, current, order_id)
    rows = (
        db.query(OrderEvent)
        .filter(OrderEvent.company_uuid == current.company_uuid, OrderEvent.order_uuid == order.uuid)
        .order_by(OrderEvent.created_at.asc().nullsfirst(), OrderEvent.id.asc())
        .all()
    )
    return rows

