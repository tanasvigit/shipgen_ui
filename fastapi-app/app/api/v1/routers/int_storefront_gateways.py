from typing import List, Optional, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_gateway import StorefrontGateway
from app.models.user import User

router = APIRouter(prefix="/int/v1/gateways", tags=["int-storefront-gateways"])


class GatewayCreate(BaseModel):
    store_uuid: str
    code: str
    name: str
    type: str
    config: Optional[dict[str, Any]] = None
    options: Optional[dict[str, Any]] = None


class GatewayUpdate(BaseModel):
    store_uuid: Optional[str] = None
    code: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    options: Optional[dict[str, Any]] = None


@router.get("/", response_model=List[dict])
def list_gateways(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    gateways = db.query(StorefrontGateway).filter(
        StorefrontGateway.company_uuid == current.company_uuid,
        StorefrontGateway.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [gw.__dict__ for gw in gateways]


@router.get("/{id}", response_model=dict)
def get_gateway(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    gateway = db.query(StorefrontGateway).filter(
        StorefrontGateway.company_uuid == current.company_uuid,
        (StorefrontGateway.uuid == id) | (StorefrontGateway.public_id == id),
        StorefrontGateway.deleted_at.is_(None)
    ).first()
    if not gateway:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gateway not found")
    return gateway.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_gateway(
    payload: GatewayCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    gateway = StorefrontGateway()
    gateway.uuid = str(uuid.uuid4())
    gateway.company_uuid = current.company_uuid
    gateway.created_by_uuid = current.uuid
    gateway.store_uuid = payload.store_uuid
    gateway.code = payload.code
    gateway.name = payload.name
    gateway.type = payload.type
    gateway.config = payload.config
    gateway.options = payload.options
    
    db.add(gateway)
    db.commit()
    db.refresh(gateway)
    return gateway.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_gateway(
    id: str,
    payload: GatewayUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    gateway = db.query(StorefrontGateway).filter(
        StorefrontGateway.company_uuid == current.company_uuid,
        (StorefrontGateway.uuid == id) | (StorefrontGateway.public_id == id),
        StorefrontGateway.deleted_at.is_(None)
    ).first()
    if not gateway:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gateway not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(gateway, field):
            setattr(gateway, field, value)
    
    db.add(gateway)
    db.commit()
    db.refresh(gateway)
    return gateway.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_gateway(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    gateway = db.query(StorefrontGateway).filter(
        StorefrontGateway.company_uuid == current.company_uuid,
        (StorefrontGateway.uuid == id) | (StorefrontGateway.public_id == id),
        StorefrontGateway.deleted_at.is_(None)
    ).first()
    if not gateway:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gateway not found")
    
    gateway.deleted_at = datetime.utcnow()
    db.add(gateway)
    db.commit()
    return gateway.__dict__

