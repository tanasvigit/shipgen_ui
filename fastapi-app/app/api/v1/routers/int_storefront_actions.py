from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_store import StorefrontStore
from app.models.order import Order
from app.models.contact import Contact
from app.models.user import User

router = APIRouter(prefix="/int/v1/actions", tags=["int-storefront-actions"])


@router.get("/store-count", response_model=dict)
def get_store_count(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    count = db.query(StorefrontStore).filter(
        StorefrontStore.company_uuid == current.company_uuid,
        StorefrontStore.deleted_at.is_(None)
    ).count()
    return {"storeCount": count}


@router.get("/metrics", response_model=dict)
def get_metrics(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    store: Optional[str] = Query(None),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
):
    if not start:
        start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if not end:
        end = datetime.now()
    
    metrics = {
        "orders_count": 0,
        "customers_count": 0,
        "stores_count": 0,
        "earnings_sum": 0,
    }
    
    if not store:
        return metrics
    
    store_obj = db.query(StorefrontStore).filter(
        StorefrontStore.company_uuid == current.company_uuid,
        (StorefrontStore.uuid == store) | (StorefrontStore.public_id == store),
        StorefrontStore.deleted_at.is_(None)
    ).first()
    
    if not store_obj:
        return metrics
    
    metrics["currency"] = store_obj.currency
    
    # Orders count
    orders_count = db.query(Order).filter(
        Order.company_uuid == current.company_uuid,
        Order.type == "storefront",
        Order.deleted_at.is_(None),
        func.json_extract(Order.meta, "$.storefront_id") == store_obj.public_id,
        Order.status.notin_(["canceled"]),
        Order.created_at >= start,
        Order.created_at <= end
    ).count()
    metrics["orders_count"] = orders_count
    
    # Customers count - customers who have orders for this store
    customer_uuids = db.query(Order.customer_uuid).filter(
        Order.company_uuid == current.company_uuid,
        Order.type == "storefront",
        func.json_extract(Order.meta, "$.storefront_id") == store_obj.public_id,
        Order.status.notin_(["canceled"]),
        Order.created_at >= start,
        Order.created_at <= end,
        Order.deleted_at.is_(None)
    ).distinct().subquery()
    
    customers_count = db.query(Contact).filter(
        Contact.company_uuid == current.company_uuid,
        Contact.type == "customer",
        Contact.uuid.in_(db.query(customer_uuids.c.customer_uuid))
    ).count()
    metrics["customers_count"] = customers_count
    
    # Stores count
    stores_count = db.query(StorefrontStore).filter(
        StorefrontStore.company_uuid == current.company_uuid,
        StorefrontStore.deleted_at.is_(None)
    ).count()
    metrics["stores_count"] = stores_count
    
    # Earnings sum - sum of meta.total from orders
    orders = db.query(Order).filter(
        Order.company_uuid == current.company_uuid,
        Order.type == "storefront",
        func.json_extract(Order.meta, "$.storefront_id") == store_obj.public_id,
        Order.status.notin_(["canceled"]),
        Order.created_at >= start,
        Order.created_at <= end,
        Order.deleted_at.is_(None)
    ).all()
    
    earnings_sum = 0
    for order in orders:
        if order.meta and "total" in order.meta:
            earnings_sum += float(order.meta.get("total", 0))
    metrics["earnings_sum"] = earnings_sum
    
    return metrics


from pydantic import BaseModel

class PushNotificationRequest(BaseModel):
    title: str
    body: str
    customers: list[str] = []
    store: str
    select_all: bool = False

@router.post("/send-push-notification", response_model=dict)
def send_push_notification(
    payload: PushNotificationRequest,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    title = payload.title
    body = payload.body
    customer_ids = payload.customers
    store_id = payload.store
    select_all = payload.select_all
    
    if not title or not body:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title and body are required")
    
    if not select_all and not customer_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one customer must be selected")
    
    store = db.query(StorefrontStore).filter(
        StorefrontStore.company_uuid == current.company_uuid,
        (StorefrontStore.uuid == store_id) | (StorefrontStore.public_id == store_id),
        StorefrontStore.deleted_at.is_(None)
    ).first()
    
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    
    if select_all:
        customers = db.query(Contact).filter(
            Contact.company_uuid == current.company_uuid,
            Contact.type == "customer",
            Contact.deleted_at.is_(None)
        ).all()
    else:
        customers = db.query(Contact).filter(
            Contact.company_uuid == current.company_uuid,
            Contact.type == "customer",
            Contact.uuid.in_(customer_ids),
            Contact.deleted_at.is_(None)
        ).all()
    
    # Get device tokens for customers
    from app.models.user_device import UserDevice
    from app.utils.push_notifications import push_service
    
    device_tokens = []
    for customer in customers:
        # Get devices for customer (assuming customer has user_device records)
        devices = db.query(UserDevice).filter(
            UserDevice.user_uuid == customer.uuid,
            UserDevice.deleted_at.is_(None)
        ).all()
        for device in devices:
            if device.token:
                device_tokens.append(device.token)
    
    # Send push notifications
    if device_tokens:
        result = push_service.send_to_devices(
            registration_ids=device_tokens,
            title=title,
            body=body,
            data={
                "store_id": store.public_id,
                "type": "storefront_notification"
            }
        )
        sent_count = result.get("success_count", len(device_tokens)) if result.get("success") else 0
    else:
        sent_count = 0
    
    return {
        "status": "OK",
        "sent_count": sent_count,
        "total": len(customers),
        "devices_notified": len(device_tokens)
    }

