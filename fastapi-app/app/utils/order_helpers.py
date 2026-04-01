"""
Order helper utilities for storefront orders.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.activity import Activity
from app.models.driver import Driver


def patch_order_config(order: Order, config: Dict[str, Any]) -> Order:
    """Update order configuration (meta/options)."""
    if "meta" in config:
        if order.meta:
            order.meta.update(config["meta"])
        else:
            order.meta = config["meta"]
    
    if "options" in config:
        if order.options:
            order.options.update(config["options"])
        else:
            order.options = config["options"]
    
    order.updated_at = datetime.now(timezone.utc)
    return order


def create_order_activity(
    db: Session,
    order: Order,
    event: str,
    description: str,
    causer_uuid: Optional[str] = None,
    causer_type: str = "user",
    properties: Optional[Dict[str, Any]] = None
) -> Activity:
    """Create an activity log entry for an order."""
    activity = Activity(
        uuid=str(uuid.uuid4()),
        log_name="order",
        description=description,
        subject_type="order",
        subject_id=order.uuid,
        event=event,
        causer_type=causer_type,
        causer_id=causer_uuid,
        properties=properties or {},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(activity)
    return activity


def assign_driver_to_order(
    db: Session,
    order: Order,
    driver_uuid: str
) -> bool:
    """Assign a driver to an order."""
    # Verify driver exists and belongs to same company
    driver = db.query(Driver).filter(
        Driver.uuid == driver_uuid,
        Driver.company_uuid == order.company_uuid,
        Driver.deleted_at.is_(None)
    ).first()
    
    if not driver:
        return False
    
    order.driver_assigned_uuid = driver_uuid
    order.vehicle_assigned_uuid = driver.vehicle_uuid
    order.updated_at = datetime.now(timezone.utc)
    
    return True

