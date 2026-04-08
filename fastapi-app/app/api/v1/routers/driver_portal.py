from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.api.v1.routers.fleetops_order_flow import TransitionOrderRequest, transition_order
from app.api.v1.routers.fleetops_orders import _driver_uuid_for_user, _get_scoped_order
from app.core.company_scope import require_company_uuid
from app.core.database import get_db
from app.core.roles import DRIVER, require_roles
from app.models.driver import Driver
from app.models.order import Order
from app.models.user import User
from app.schemas.driver import DriverOut, DriverResponse
from app.schemas.order import OrderOut, OrderResponse, OrdersResponse

router = APIRouter(prefix="/driver", tags=["driver-portal"])

DRIVER_PROOF_ALLOWED_STATUSES = {"delivered", "completed"}


class DriverLocationBody(BaseModel):
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    heading: Optional[str] = None
    speed: Optional[str] = None
    altitude: Optional[str] = None
    online: Optional[int] = None


def _driver_for_current_user(db: Session, current: User) -> Driver:
    company_uuid = require_company_uuid(current)
    driver_uuid = _driver_uuid_for_user(db, current)
    if not driver_uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver profile not found for current user.",
        )
    driver = (
        db.query(Driver)
        .filter(
            Driver.company_uuid == company_uuid,
            Driver.deleted_at.is_(None),
            Driver.uuid == driver_uuid,
        )
        .first()
    )
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver profile not found for current user.",
        )
    return driver


@router.get("/orders", response_model=OrdersResponse)
def list_driver_orders(
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(DRIVER)),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    company_uuid = require_company_uuid(current)
    driver = _driver_for_current_user(db, current)
    rows = (
        db.query(Order)
        .filter(
            Order.company_uuid == company_uuid,
            Order.deleted_at.is_(None),
            Order.driver_assigned_uuid == driver.uuid,
        )
        .order_by(Order.created_at.desc().nullslast(), Order.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return OrdersResponse(orders=[OrderOut.model_validate(x) for x in rows])


@router.get("/orders/history", response_model=OrdersResponse)
def list_driver_order_history(
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(DRIVER)),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    company_uuid = require_company_uuid(current)
    driver = _driver_for_current_user(db, current)
    rows = (
        db.query(Order)
        .filter(
            Order.company_uuid == company_uuid,
            Order.deleted_at.is_(None),
            Order.driver_assigned_uuid == driver.uuid,
            Order.status == "completed",
        )
        .order_by(Order.updated_at.desc().nullslast(), Order.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return OrdersResponse(orders=[OrderOut.model_validate(x) for x in rows])


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_driver_order(
    order_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(DRIVER)),
):
    order = _get_scoped_order(db, current, order_id)
    return OrderResponse(order=OrderOut.model_validate(order))


@router.post("/orders/{order_id}/transition", response_model=OrderResponse)
def transition_driver_order(
    order_id: str,
    payload: TransitionOrderRequest,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(DRIVER)),
):
    # Reuse centralized transition validation; role=DRIVER branch is enforced there.
    return transition_order(order_id=order_id, payload=payload, db=db, current=current)


@router.post("/orders/{order_id}/proof", response_model=OrderResponse)
async def upload_driver_order_proof(
    order_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(DRIVER)),
    otp: str | None = Form(default=None),
    signature: str | None = Form(default=None),
    proof_file: UploadFile | None = File(default=None),
):
    order = _get_scoped_order(db, current, order_id)
    status_now = (order.status or "").strip().lower()
    if status_now not in DRIVER_PROOF_ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Proof is allowed only for statuses: {sorted(DRIVER_PROOF_ALLOWED_STATUSES)}",
        )

    file_meta: dict[str, Any] | None = None
    if proof_file is not None:
        content = await proof_file.read()
        file_meta = {
            "filename": proof_file.filename,
            "content_type": proof_file.content_type,
            "size_bytes": len(content),
        }

    if not (otp or signature or file_meta):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one proof artifact is required: otp, signature, or proof_file.",
        )

    meta = dict(order.meta or {})
    meta["proof_of_delivery"] = {
        "uploaded_by_driver_uuid": _driver_for_current_user(db, current).uuid,
        "uploaded_at": datetime.utcnow().isoformat(),
        "otp": otp.strip() if otp else None,
        "signature": signature.strip() if signature else None,
        "file": file_meta,
    }
    order.meta = meta
    order.updated_at = datetime.utcnow()
    db.add(order)
    db.commit()
    db.refresh(order)
    return OrderResponse(order=OrderOut.model_validate(order))


@router.post("/location", response_model=DriverResponse)
def update_driver_location(
    payload: DriverLocationBody,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(DRIVER)),
):
    driver = _driver_for_current_user(db, current)
    if payload.latitude is not None:
        driver.latitude = payload.latitude
    if payload.longitude is not None:
        driver.longitude = payload.longitude
    if payload.heading is not None:
        driver.heading = payload.heading
    if payload.speed is not None:
        driver.speed = payload.speed
    if payload.altitude is not None:
        driver.altitude = payload.altitude
    if payload.online is not None:
        if payload.online not in (0, 1):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="online must be 0 or 1")
        driver.online = payload.online

    db.add(driver)
    db.commit()
    db.refresh(driver)
    return DriverResponse(driver=DriverOut.model_validate(driver))


class DriverOnlineBody(BaseModel):
    """Request body for setting driver online/offline status."""
    online: Optional[int] = 1
    status: Optional[str] = None


@router.post("/online", response_model=DriverResponse)
def set_driver_online(
    payload: DriverOnlineBody,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(DRIVER)),
):
    """
    Set driver online status after login.
    
    This endpoint should be called immediately after a DRIVER logs in
    to mark them as available for order assignments.
    
    - Updates `online` field (1 = online, 0 = offline)
    - Updates `status` to 'active' if provided
    - Updates `last_seen_at` timestamp to current time
    """
    driver = _driver_for_current_user(db, current)
    
    # Update online status
    if payload.online is not None:
        if payload.online not in (0, 1):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="online must be 0 or 1")
        driver.online = payload.online
    
    # Update status if provided
    if payload.status is not None:
        driver.status = payload.status
    
    # Always update last_seen_at timestamp
    driver.last_seen_at = datetime.utcnow()
    
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return DriverResponse(driver=DriverOut.model_validate(driver))
