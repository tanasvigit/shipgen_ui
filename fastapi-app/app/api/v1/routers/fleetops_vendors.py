from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorOut, VendorUpdate, VendorResponse, VendorsResponse

router = APIRouter(prefix="/fleetops/v1/vendors", tags=["fleetops-vendors"])


@router.get("/", response_model=VendorsResponse)
def list_vendors(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    q = db.query(Vendor).filter(Vendor.company_uuid == current.company_uuid, Vendor.deleted_at.is_(None))
    vendors = q.offset(offset).limit(limit).all()
    return {"vendors": vendors}


@router.get("/{id}", response_model=VendorResponse)
def get_vendor(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    vendor = (
        db.query(Vendor)
        .filter(Vendor.company_uuid == current.company_uuid, (Vendor.uuid == id) | (Vendor.public_id == id))
        .first()
    )
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found.")
    return {"vendor": vendor}


@router.post("/", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def create_vendor(
    payload: VendorCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    vendor = Vendor()
    vendor.uuid = str(uuid.uuid4())
    vendor.public_id = f"vendor_{uuid.uuid4().hex[:12]}"
    vendor.company_uuid = current.company_uuid
    vendor.name = payload.name
    vendor.type = payload.type
    vendor.email = payload.email
    vendor.phone = payload.phone
    vendor.meta = payload.meta

    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return {"vendor": vendor}


@router.put("/{id}", response_model=VendorResponse)
@router.patch("/{id}", response_model=VendorResponse)
def update_vendor(
    id: str,
    payload: VendorUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    vendor = (
        db.query(Vendor)
        .filter(Vendor.company_uuid == current.company_uuid, (Vendor.uuid == id) | (Vendor.public_id == id))
        .first()
    )
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found.")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(vendor, field, value)

    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return {"vendor": vendor}


@router.delete("/{id}", response_model=VendorResponse)
def delete_vendor(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    vendor = (
        db.query(Vendor)
        .filter(Vendor.company_uuid == current.company_uuid, (Vendor.uuid == id) | (Vendor.public_id == id))
        .first()
    )
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found.")

    vendor.deleted_at = datetime.utcnow()
    db.add(vendor)
    db.commit()
    return {"vendor": vendor}



