from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_store import StorefrontStore
from app.models.storefront_store_location import StorefrontStoreLocation
from app.models.storefront_gateway import StorefrontGateway
from app.models.user import User
from app.schemas.storefront_store import StoreOut
from app.schemas.storefront_store_location import StoreLocationOut
from app.schemas.storefront_gateway import GatewayOut

router = APIRouter(prefix="/storefront/v1", tags=["storefront-stores"])


@router.get("/about", response_model=StoreOut)
def get_about(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Get storefront_store or storefront_network from session (simplified)
    # In production, this would come from session/headers
    store = (
        db.query(StorefrontStore)
        .filter(StorefrontStore.company_uuid == current.company_uuid)
        .first()
    )
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unable to find store!")
    return store


@router.get("/lookup/{id}", response_model=StoreOut)
def lookup_store(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    store = (
        db.query(StorefrontStore)
        .filter(StorefrontStore.company_uuid == current.company_uuid, (StorefrontStore.uuid == id) | (StorefrontStore.public_id == id))
        .first()
    )
    if store:
        return store
    
    from app.models.storefront_network import StorefrontNetwork
    network = (
        db.query(StorefrontNetwork)
        .filter(StorefrontNetwork.company_uuid == current.company_uuid, (StorefrontNetwork.uuid == id) | (StorefrontNetwork.public_id == id))
        .first()
    )
    if network:
        return network
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unable to find store or network for ID provided.")


@router.get("/locations", response_model=List[StoreLocationOut])
def list_locations(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    store: Optional[str] = None,
):
    query = db.query(StorefrontStoreLocation)
    
    if store:
        store_obj = (
            db.query(StorefrontStore)
            .filter(StorefrontStore.company_uuid == current.company_uuid, (StorefrontStore.uuid == store) | (StorefrontStore.public_id == store))
            .first()
        )
        if store_obj:
            query = query.filter(StorefrontStoreLocation.store_uuid == store_obj.uuid)
    
    locations = query.all()
    return locations


@router.get("/locations/{id}", response_model=StoreLocationOut)
def get_location(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    store: Optional[str] = None,
):
    store_id = store
    store_obj = None
    if store_id:
        store_obj = (
            db.query(StorefrontStore)
            .filter(StorefrontStore.company_uuid == current.company_uuid, (StorefrontStore.uuid == store_id) | (StorefrontStore.public_id == store_id))
            .first()
        )
    
    query = db.query(StorefrontStoreLocation).filter(
        (StorefrontStoreLocation.uuid == id) | (StorefrontStoreLocation.public_id == id)
    )
    
    if store_obj:
        query = query.filter(StorefrontStoreLocation.store_uuid == store_obj.uuid)
    
    location = query.first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found.")
    return location


@router.get("/gateways", response_model=List[GatewayOut])
def list_gateways(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    sandbox: bool = Query(False),
):
    # Get storefront_store or storefront_network from session (simplified)
    owner_uuid = None  # Would come from session
    
    query = db.query(StorefrontGateway).filter(StorefrontGateway.owner_uuid == owner_uuid)
    
    if sandbox:
        query = query.filter(StorefrontGateway.sandbox == True)
    
    gateways = query.all()
    
    # Add cash gateway if COD enabled (simplified)
    # In production, check store/network options
    
    return gateways


@router.get("/gateways/{id}", response_model=GatewayOut)
def get_gateway(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    gateway = (
        db.query(StorefrontGateway)
        .filter((StorefrontGateway.uuid == id) | (StorefrontGateway.public_id == id))
        .first()
    )
    if not gateway:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gateway not found.")
    return gateway


@router.get("/search", response_model=List[StoreOut])
def search_stores(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    query: Optional[str] = None,
):
    stores = (
        db.query(StorefrontStore)
        .filter(StorefrontStore.company_uuid == current.company_uuid)
        .all()
    )
    # In production, would implement full-text search
    return stores

