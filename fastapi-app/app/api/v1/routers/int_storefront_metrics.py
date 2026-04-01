from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import func

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.order import Order
from app.models.contact import Contact
from app.models.storefront_store import StorefrontStore

router = APIRouter(prefix="/int/v1/metrics", tags=["int-storefront-metrics"])


@router.get("/", response_model=dict)
def get_all_metrics(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    discover: Optional[List[str]] = Query(None),
):
    """Get comprehensive metrics for the company."""
    # Default to last 30 days if not specified
    if not end:
        end = datetime.now()
    if not start:
        start = end - timedelta(days=30)
    
    # Base query filters
    base_filters = [
        Order.company_uuid == current.company_uuid,
        Order.type == "storefront",
        Order.deleted_at.is_(None),
        Order.created_at >= start,
        Order.created_at <= end
    ]
    
    # Order metrics
    total_orders = db.query(Order).filter(*base_filters).count()
    
    completed_orders = db.query(Order).filter(
        *base_filters,
        Order.status == "completed"
    ).count()
    
    pending_orders = db.query(Order).filter(
        *base_filters,
        Order.status == "pending"
    ).count()
    
    # Revenue calculation
    orders = db.query(Order).filter(*base_filters).all()
    total_revenue = 0.0
    for order in orders:
        if order.meta and "total" in order.meta:
            try:
                total_revenue += float(order.meta.get("total", 0))
            except (ValueError, TypeError):
                pass
    
    # Customer metrics
    unique_customers = db.query(func.count(func.distinct(Order.customer_uuid))).filter(
        *base_filters,
        Order.customer_uuid.isnot(None)
    ).scalar() or 0
    
    total_customers = db.query(Contact).filter(
        Contact.company_uuid == current.company_uuid,
        Contact.type == "customer",
        Contact.deleted_at.is_(None)
    ).count()
    
    # Store metrics
    total_stores = db.query(StorefrontStore).filter(
        StorefrontStore.company_uuid == current.company_uuid,
        StorefrontStore.deleted_at.is_(None)
    ).count()
    
    # Build response
    metrics = {
        "company_uuid": str(current.company_uuid),
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat()
        },
        "orders": {
            "total": total_orders,
            "completed": completed_orders,
            "pending": pending_orders,
            "cancelled": db.query(Order).filter(
                *base_filters,
                Order.status == "cancelled"
            ).count()
        },
        "revenue": {
            "total": total_revenue,
            "currency": "USD"  # Default, should come from company settings
        },
        "customers": {
            "total": total_customers,
            "active": unique_customers,
            "new": db.query(Contact).filter(
                Contact.company_uuid == current.company_uuid,
                Contact.type == "customer",
                Contact.created_at >= start,
                Contact.created_at <= end,
                Contact.deleted_at.is_(None)
            ).count()
        },
        "stores": {
            "total": total_stores
        }
    }
    
    # Add discovered metrics if requested
    if discover:
        discovered = {}
        for metric_name in discover:
            if metric_name == "orders_by_status":
                status_counts = {}
                for status in ["pending", "accepted", "preparing", "dispatched", "completed", "cancelled"]:
                    status_counts[status] = db.query(Order).filter(
                        *base_filters,
                        Order.status == status
                    ).count()
                discovered["orders_by_status"] = status_counts
        metrics["discovered"] = discovered
    
    return metrics

