from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_network import StorefrontNetwork
from app.models.storefront_network_store import StorefrontNetworkStore
from app.models.storefront_store import StorefrontStore
from app.models.category import Category
from app.models.user import User

router = APIRouter(prefix="/int/v1/networks", tags=["int-storefront-networks"])


class NetworkCreate(BaseModel):
    name: str
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    tags: Optional[list[str]] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    options: Optional[dict[str, Any]] = None
    online: Optional[bool] = True


class NetworkUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    tags: Optional[list[str]] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    options: Optional[dict[str, Any]] = None
    online: Optional[bool] = None


class AddStoresRequest(BaseModel):
    stores: List[str]


class SetStoreCategoryRequest(BaseModel):
    store: str
    category: Optional[str] = None


class RemoveStoreCategoryRequest(BaseModel):
    store: str


@router.get("/", response_model=List[dict])
def list_networks(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    q = db.query(StorefrontNetwork).filter(StorefrontNetwork.company_uuid == current.company_uuid, StorefrontNetwork.deleted_at.is_(None))
    networks = q.offset(offset).limit(limit).all()
    return [network.__dict__ for network in networks]


@router.get("/find/{id}", response_model=dict)
def find_network(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    network = (
        db.query(StorefrontNetwork)
        .filter(StorefrontNetwork.company_uuid == current.company_uuid, (StorefrontNetwork.uuid == id) | (StorefrontNetwork.public_id == id))
        .first()
    )
    if not network:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Network not found.")
    return network.__dict__


@router.get("/{id}", response_model=dict)
def get_network(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    network = (
        db.query(StorefrontNetwork)
        .filter(StorefrontNetwork.company_uuid == current.company_uuid, (StorefrontNetwork.uuid == id) | (StorefrontNetwork.public_id == id))
        .first()
    )
    if not network:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Network not found.")
    return network.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_network(
    payload: NetworkCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    network = StorefrontNetwork()
    network.uuid = str(uuid.uuid4())
    network.company_uuid = current.company_uuid
    network.created_by_uuid = current.uuid
    network.name = payload.name
    network.description = payload.description
    network.phone = payload.phone
    network.email = payload.email
    network.website = payload.website
    network.facebook = payload.facebook
    network.instagram = payload.instagram
    network.twitter = payload.twitter
    network.tags = payload.tags
    network.currency = payload.currency
    network.timezone = payload.timezone
    network.options = payload.options
    network.online = payload.online
    
    db.add(network)
    db.commit()
    db.refresh(network)
    return network.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_network(
    id: str,
    payload: NetworkUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    network = (
        db.query(StorefrontNetwork)
        .filter(StorefrontNetwork.company_uuid == current.company_uuid, (StorefrontNetwork.uuid == id) | (StorefrontNetwork.public_id == id))
        .first()
    )
    if not network:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Network not found.")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(network, field):
            setattr(network, field, value)
    
    db.add(network)
    db.commit()
    db.refresh(network)
    return network.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_network(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    network = (
        db.query(StorefrontNetwork)
        .filter(StorefrontNetwork.company_uuid == current.company_uuid, (StorefrontNetwork.uuid == id) | (StorefrontNetwork.public_id == id))
        .first()
    )
    if not network:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Network not found.")
    
    network.deleted_at = datetime.utcnow()
    db.add(network)
    db.commit()
    return network.__dict__


@router.post("/{id}/add-stores", response_model=dict)
def add_stores_to_network(
    id: str,
    payload: AddStoresRequest,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    network = (
        db.query(StorefrontNetwork)
        .filter(StorefrontNetwork.company_uuid == current.company_uuid, (StorefrontNetwork.uuid == id) | (StorefrontNetwork.public_id == id))
        .first()
    )
    if not network:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Network not found.")
    
    store_ids = payload.stores
    
    for store_id in store_ids:
        store = (
            db.query(StorefrontStore)
            .filter(StorefrontStore.company_uuid == current.company_uuid, (StorefrontStore.uuid == store_id) | (StorefrontStore.public_id == store_id))
            .first()
        )
        if store:
            # Check if already exists
            existing = (
                db.query(StorefrontNetworkStore)
                .filter(StorefrontNetworkStore.network_uuid == network.uuid, StorefrontNetworkStore.store_uuid == store.uuid)
                .first()
            )
            if not existing:
                ns = StorefrontNetworkStore()
                ns.uuid = str(uuid.uuid4())
                ns.network_uuid = network.uuid
                ns.store_uuid = store.uuid
                db.add(ns)
    
    db.commit()
    return {"message": "Stores added successfully"}


@router.post("/{id}/remove-stores", response_model=dict)
def remove_stores_from_network(
    id: str,
    payload: AddStoresRequest,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    network = (
        db.query(StorefrontNetwork)
        .filter(StorefrontNetwork.company_uuid == current.company_uuid, (StorefrontNetwork.uuid == id) | (StorefrontNetwork.public_id == id))
        .first()
    )
    if not network:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Network not found.")
    
    store_ids = payload.stores
    
    for store_id in store_ids:
        store = (
            db.query(StorefrontStore)
            .filter(StorefrontStore.company_uuid == current.company_uuid, (StorefrontStore.uuid == store_id) | (StorefrontStore.public_id == store_id))
            .first()
        )
        if store:
            ns = (
                db.query(StorefrontNetworkStore)
                .filter(StorefrontNetworkStore.network_uuid == network.uuid, StorefrontNetworkStore.store_uuid == store.uuid)
                .first()
            )
            if ns:
                ns.deleted_at = datetime.utcnow()
                db.add(ns)
    
    db.commit()
    return {"message": "Stores removed successfully"}


@router.post("/{id}/set-store-category", response_model=dict)
def set_store_category(
    id: str,
    payload: SetStoreCategoryRequest,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    network = (
        db.query(StorefrontNetwork)
        .filter(StorefrontNetwork.company_uuid == current.company_uuid, (StorefrontNetwork.uuid == id) | (StorefrontNetwork.public_id == id))
        .first()
    )
    if not network:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Network not found.")
    
    store_id = payload.store
    category_id = payload.category
    
    store = (
        db.query(StorefrontStore)
        .filter(StorefrontStore.company_uuid == current.company_uuid, (StorefrontStore.uuid == store_id) | (StorefrontStore.public_id == store_id))
        .first()
    )
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found.")
    
    category = None
    if category_id:
        category = (
            db.query(Category)
            .filter((Category.uuid == category_id) | (Category.public_id == category_id))
            .first()
        )
    
    ns = (
        db.query(StorefrontNetworkStore)
        .filter(StorefrontNetworkStore.network_uuid == network.uuid, StorefrontNetworkStore.store_uuid == store.uuid)
        .first()
    )
    if ns:
        ns.category_uuid = category.uuid if category else None
        db.add(ns)
    else:
        ns = StorefrontNetworkStore()
        ns.uuid = str(uuid.uuid4())
        ns.network_uuid = network.uuid
        ns.store_uuid = store.uuid
        ns.category_uuid = category.uuid if category else None
        db.add(ns)
    
    db.commit()
    return {"message": "Store category set successfully"}


@router.delete("/{id}/remove-category", response_model=dict)
def remove_store_category(
    id: str,
    payload: RemoveStoreCategoryRequest,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    network = (
        db.query(StorefrontNetwork)
        .filter(StorefrontNetwork.company_uuid == current.company_uuid, (StorefrontNetwork.uuid == id) | (StorefrontNetwork.public_id == id))
        .first()
    )
    if not network:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Network not found.")
    
    store_id = payload.store
    
    store = (
        db.query(StorefrontStore)
        .filter(StorefrontStore.company_uuid == current.company_uuid, (StorefrontStore.uuid == store_id) | (StorefrontStore.public_id == store_id))
        .first()
    )
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found.")
    
    ns = (
        db.query(StorefrontNetworkStore)
        .filter(StorefrontNetworkStore.network_uuid == network.uuid, StorefrontNetworkStore.store_uuid == store.uuid)
        .first()
    )
    if ns:
        ns.category_uuid = None
        db.add(ns)
        db.commit()
    
    return {"message": "Store category removed successfully"}


@router.post("/{id}/invite", response_model=dict)
def send_invites(
    id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    network = (
        db.query(StorefrontNetwork)
        .filter(StorefrontNetwork.company_uuid == current.company_uuid, (StorefrontNetwork.uuid == id) | (StorefrontNetwork.public_id == id))
        .first()
    )
    if not network:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Network not found.")
    
    # Extract invite data
    emails = payload.get("emails", [])
    phones = payload.get("phones", [])
    message = payload.get("message", f"You've been invited to join {network.name}")
    
    from app.utils.verification import send_verification_email, send_verification_sms
    from app.models.contact import Contact
    
    sent_count = 0
    errors = []
    
    # Generate invite token
    import secrets
    invite_token = secrets.token_urlsafe(32)
    invite_url = f"{os.getenv('APP_URL', 'http://localhost:9001')}/networks/{network.public_id}/join?token={invite_token}"
    
    # Store invite token in network options
    if not network.options:
        network.options = {}
    network.options["invite_token"] = invite_token
    network.options["invite_url"] = invite_url
    db.add(network)
    
    # Send email invites
    for email in emails:
        try:
            # Check if contact exists
            contact = db.query(Contact).filter(
                Contact.email == email,
                Contact.company_uuid == current.company_uuid,
                Contact.deleted_at.is_(None)
            ).first()
            
            if not contact:
                # Create contact
                contact = Contact(
                    uuid=str(uuid.uuid4()),
                    public_id=f"contact_{uuid.uuid4().hex[:12]}",
                    company_uuid=current.company_uuid,
                    email=email,
                    type="customer",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                db.add(contact)
                db.flush()
            
            # Send email with invite link
            email_body = f"{message}\n\nJoin here: {invite_url}"
            send_verification_email(email, email_body)  # Reuse email function
            sent_count += 1
        except Exception as e:
            errors.append({"email": email, "error": str(e)})
    
    # Send SMS invites
    for phone in phones:
        try:
            contact = db.query(Contact).filter(
                Contact.phone == phone,
                Contact.company_uuid == current.company_uuid,
                Contact.deleted_at.is_(None)
            ).first()
            
            if not contact:
                contact = Contact(
                    uuid=str(uuid.uuid4()),
                    public_id=f"contact_{uuid.uuid4().hex[:12]}",
                    company_uuid=current.company_uuid,
                    phone=phone,
                    type="customer",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                db.add(contact)
                db.flush()
            
            sms_body = f"{message} Join: {invite_url}"
            send_verification_sms(phone, sms_body)  # Reuse SMS function
            sent_count += 1
        except Exception as e:
            errors.append({"phone": phone, "error": str(e)})
    
    db.commit()
    
    return {
        "message": "Invites sent successfully",
        "network_id": network.public_id,
        "sent_count": sent_count,
        "errors": errors
    }

