from typing import List
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.entity import Entity
from app.models.payload import Payload
from app.models.contact import Contact
from app.models.vendor import Vendor
from app.models.driver import Driver
from app.models.user import User
from app.schemas.entity import EntityCreate, EntityOut, EntityUpdate, EntityResponse, EntitiesResponse

router = APIRouter(prefix="/fleetops/v1/entities", tags=["fleetops-entities"])


@router.get("/", response_model=EntitiesResponse)
def list_entities(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    q = db.query(Entity).filter(Entity.company_uuid == current.company_uuid, Entity.deleted_at.is_(None))
    entities = q.offset(offset).limit(limit).all()
    return {"entities": entities}


@router.get("/{id}", response_model=EntityResponse)
def get_entity(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    entity = (
        db.query(Entity)
        .filter(Entity.company_uuid == current.company_uuid, (Entity.uuid == id) | (Entity.public_id == id))
        .first()
    )
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found.")
    return {"entity": entity}


@router.post("/", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_entity(
    payload: EntityCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    entity = Entity()
    entity.uuid = str(uuid.uuid4())
    entity.public_id = f"entity_{uuid.uuid4().hex[:12]}"
    entity.company_uuid = current.company_uuid
    entity.name = payload.name
    entity.type = payload.type
    entity.internal_id = payload.internal_id
    entity.description = payload.description
    entity.meta = payload.meta
    entity.length = payload.length
    entity.width = payload.width
    entity.height = payload.height
    entity.weight = payload.weight
    entity.weight_unit = payload.weight_unit
    entity.dimensions_unit = payload.dimensions_unit
    entity.declared_value = payload.declared_value
    entity.price = payload.price
    entity.sale_price = payload.sales_price
    entity.sku = payload.sku
    entity.currency = payload.currency
    entity.supplier_uuid = payload.supplier_uuid

    # Handle payload assignment
    if payload.payload:
        payload_obj = (
            db.query(Payload)
            .filter(Payload.company_uuid == current.company_uuid, (Payload.uuid == payload.payload) | (Payload.public_id == payload.payload))
            .first()
        )
        if payload_obj:
            entity.payload_uuid = payload_obj.uuid

    # Handle customer assignment (contact or vendor)
    if payload.customer:
        customer = (
            db.query(Contact)
            .filter(Contact.company_uuid == current.company_uuid, (Contact.uuid == payload.customer) | (Contact.public_id == payload.customer))
            .first()
        )
        if not customer:
            customer = (
                db.query(Vendor)
                .filter(Vendor.company_uuid == current.company_uuid, (Vendor.uuid == payload.customer) | (Vendor.public_id == payload.customer))
                .first()
            )
        if customer:
            entity.customer_uuid = customer.uuid
            entity.customer_type = "Contact" if isinstance(customer, Contact) else "Vendor"

    # Handle driver assignment
    if payload.driver:
        driver = (
            db.query(Driver)
            .filter(Driver.company_uuid == current.company_uuid, (Driver.uuid == payload.driver) | (Driver.public_id == payload.driver))
            .first()
        )
        if driver:
            entity.driver_assigned_uuid = driver.uuid

    db.add(entity)
    db.commit()
    db.refresh(entity)
    return {"entity": entity}


@router.put("/{id}", response_model=EntityResponse)
def update_entity(
    id: str,
    payload: EntityUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    entity = (
        db.query(Entity)
        .filter(Entity.company_uuid == current.company_uuid, (Entity.uuid == id) | (Entity.public_id == id))
        .first()
    )
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found.")

    # Update basic fields
    update_data = payload.dict(exclude_unset=True, exclude={"payload", "customer", "driver", "destination", "waypoint"})
    for field, value in update_data.items():
        if field == "sales_price":
            setattr(entity, "sale_price", value)
        else:
            setattr(entity, field, value)

    # Handle payload assignment
    if payload.payload:
        payload_obj = (
            db.query(Payload)
            .filter(Payload.company_uuid == current.company_uuid, (Payload.uuid == payload.payload) | (Payload.public_id == payload.payload))
            .first()
        )
        if payload_obj:
            entity.payload_uuid = payload_obj.uuid

    # Handle customer assignment
    if payload.customer:
        customer = (
            db.query(Contact)
            .filter(Contact.company_uuid == current.company_uuid, (Contact.uuid == payload.customer) | (Contact.public_id == payload.customer))
            .first()
        )
        if not customer:
            customer = (
                db.query(Vendor)
                .filter(Vendor.company_uuid == current.company_uuid, (Vendor.uuid == payload.customer) | (Vendor.public_id == payload.customer))
                .first()
            )
        if customer:
            entity.customer_uuid = customer.uuid
            entity.customer_type = "Contact" if isinstance(customer, Contact) else "Vendor"

    # Handle driver assignment
    if payload.driver:
        driver = (
            db.query(Driver)
            .filter(Driver.company_uuid == current.company_uuid, (Driver.uuid == payload.driver) | (Driver.public_id == payload.driver))
            .first()
        )
        if driver:
            entity.driver_assigned_uuid = driver.uuid

    db.add(entity)
    db.commit()
    db.refresh(entity)
    return {"entity": entity}


@router.delete("/{id}", response_model=EntityResponse)
def delete_entity(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    entity = (
        db.query(Entity)
        .filter(Entity.company_uuid == current.company_uuid, (Entity.uuid == id) | (Entity.public_id == id))
        .first()
    )
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found.")

    entity.deleted_at = datetime.utcnow()
    db.add(entity)
    db.commit()
    return {"entity": entity}

