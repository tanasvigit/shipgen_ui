from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_network import StorefrontNetwork
from app.models.storefront_store import StorefrontStore
from app.models.storefront_network_store import StorefrontNetworkStore
from app.models.category import Category
from app.models.user import User
from app.schemas.storefront_network import NetworkOut
from app.schemas.storefront_store import StoreOut

router = APIRouter(prefix="/storefront/v1", tags=["storefront-networks"])


@router.get("/stores", response_model=List[StoreOut])
def list_network_stores(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(None, ge=1, le=100),
    offset: int = Query(None, ge=0),
    sort: Optional[str] = None,
    ids: Optional[str] = None,
    tagged: Optional[str] = None,
    query: Optional[str] = None,
    exclude: Optional[str] = None,
    without_category: bool = Query(False),
    category: Optional[str] = None,
):
    # Get storefront_network from session (simplified)
    network_uuid = None  # Would come from session
    
    # Get stores in network
    network_store_ids = (
        db.query(StorefrontNetworkStore.store_uuid)
        .filter(StorefrontNetworkStore.network_uuid == network_uuid)
        .all()
    )
    store_uuids = [ns[0] for ns in network_store_ids]
    
    query_obj = (
        db.query(StorefrontStore)
        .filter(StorefrontStore.company_uuid == current.company_uuid, StorefrontStore.uuid.in_(store_uuids))
    )
    
    # Filter by category
    if category:
        cat = (
            db.query(Category)
            .filter((Category.uuid == category) | (Category.public_id == category))
            .first()
        )
        if cat:
            network_store_ids = (
                db.query(StorefrontNetworkStore.store_uuid)
                .filter(StorefrontNetworkStore.network_uuid == network_uuid, StorefrontNetworkStore.category_uuid == cat.uuid)
                .all()
            )
            store_uuids = [ns[0] for ns in network_store_ids]
            query_obj = query_obj.filter(StorefrontStore.uuid.in_(store_uuids))
    
    if without_category:
        network_store_ids = (
            db.query(StorefrontNetworkStore.store_uuid)
            .filter(StorefrontNetworkStore.network_uuid == network_uuid, StorefrontNetworkStore.category_uuid.is_(None))
            .all()
        )
        store_uuids = [ns[0] for ns in network_store_ids]
        query_obj = query_obj.filter(StorefrontStore.uuid.in_(store_uuids))
    
    # Apply sorting
    if sort == "highest_rated":
        # Would need to join with reviews and calculate average
        pass
    elif sort == "newest":
        query_obj = query_obj.order_by(StorefrontStore.created_at.desc())
    elif sort == "oldest":
        query_obj = query_obj.order_by(StorefrontStore.created_at.asc())
    
    if limit:
        query_obj = query_obj.limit(limit)
    if offset:
        query_obj = query_obj.offset(offset)
    
    stores = query_obj.all()
    return stores


@router.get("/store-locations", response_model=List[dict])
def list_network_store_locations(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Get all store locations for stores in network
    network_uuid = None  # Would come from session
    
    network_store_ids = (
        db.query(StorefrontNetworkStore.store_uuid)
        .filter(StorefrontNetworkStore.network_uuid == network_uuid)
        .all()
    )
    store_uuids = [ns[0] for ns in network_store_ids]
    
    from app.models.storefront_store_location import StorefrontStoreLocation
    locations = (
        db.query(StorefrontStoreLocation)
        .filter(StorefrontStoreLocation.store_uuid.in_(store_uuids))
        .all()
    )
    
    return locations


@router.get("/tags", response_model=List[str])
def list_tags(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Get all unique tags from stores in network
    network_uuid = None  # Would come from session
    
    network_store_ids = (
        db.query(StorefrontNetworkStore.store_uuid)
        .filter(StorefrontNetworkStore.network_uuid == network_uuid)
        .all()
    )
    store_uuids = [ns[0] for ns in network_store_ids]
    
    stores = (
        db.query(StorefrontStore)
        .filter(StorefrontStore.uuid.in_(store_uuids))
        .all()
    )
    
    tags = set()
    for store in stores:
        if store.tags:
            if isinstance(store.tags, list):
                tags.update(store.tags)
            elif isinstance(store.tags, dict):
                tags.update(store.tags.keys())
    
    return list(tags)

