from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class EntityBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    payload_uuid: Optional[str] = None
    company_uuid: Optional[str] = None
    driver_assigned_uuid: Optional[str] = None
    destination_uuid: Optional[str] = None
    customer_uuid: Optional[str] = None
    customer_type: Optional[str] = None
    tracking_number_uuid: Optional[str] = None
    photo_uuid: Optional[str] = None
    supplier_uuid: Optional[str] = None
    category_uuid: Optional[str] = None
    internal_id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    currency: Optional[str] = None
    barcode: Optional[str] = None
    qr_code: Optional[str] = None
    weight: Optional[str] = None
    weight_unit: Optional[str] = None
    length: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    dimensions_unit: Optional[str] = None
    declared_value: Optional[int] = None
    sku: Optional[str] = None
    price: Optional[str] = None
    sale_price: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    slug: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EntityCreate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    internal_id: Optional[str] = None
    description: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    length: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    weight_unit: Optional[str] = None
    dimensions_unit: Optional[str] = None
    declared_value: Optional[int] = None
    price: Optional[str] = None
    sales_price: Optional[str] = None
    sku: Optional[str] = None
    currency: Optional[str] = None
    payload: Optional[str] = None  # public_id
    customer: Optional[str] = None  # public_id
    driver: Optional[str] = None  # public_id
    destination: Optional[str] = None  # waypoint key
    waypoint: Optional[str] = None  # waypoint key
    supplier_uuid: Optional[str] = None


class EntityUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    internal_id: Optional[str] = None
    description: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    length: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    weight_unit: Optional[str] = None
    dimensions_unit: Optional[str] = None
    declared_value: Optional[int] = None
    price: Optional[str] = None
    sales_price: Optional[str] = None
    sku: Optional[str] = None
    currency: Optional[str] = None
    payload: Optional[str] = None  # public_id
    customer: Optional[str] = None  # public_id
    driver: Optional[str] = None  # public_id
    destination: Optional[str] = None  # waypoint key
    waypoint: Optional[str] = None  # waypoint key
    supplier_uuid: Optional[str] = None




class EntityOut(EntityBase):
    id: Optional[int] = None
    customer_is_vendor: Optional[bool] = None
    customer_is_contact: Optional[bool] = None
    tracking: Optional[dict[str, Any]] = None
    status: Optional[str] = None
    photo_url: Optional[str] = None

    class Config:
        from_attributes = True


class EntityResponse(BaseModel):
    entity: EntityOut


class EntitiesResponse(BaseModel):
    entities: List[EntityOut]

