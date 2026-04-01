"""
Pydantic schemas for Storefront (customers, products, carts, orders).
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# Customer schemas (uses Contact with type='customer')
class CustomerBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    meta: Optional[dict] = None


class CustomerCreate(CustomerBase):
    password: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    meta: Optional[dict] = None


class CustomerOut(CustomerBase):
    uuid: str
    public_id: str
    company_uuid: Optional[str] = None
    type: str = "customer"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerLoginRequest(BaseModel):
    identity: str = Field(..., description="Email or phone")
    password: str


# Product schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    sku: Optional[str] = None
    price: int = Field(..., description="Price in cents")
    sale_price: int = Field(default=0, description="Sale price in cents")
    currency: Optional[str] = "USD"
    is_service: bool = False
    is_bookable: bool = False
    is_available: bool = True
    is_on_sale: bool = False
    is_recommended: bool = False
    can_pickup: bool = False
    status: Optional[str] = "available"
    meta: Optional[dict] = None
    youtube_urls: Optional[List[str]] = None


class ProductCreate(ProductBase):
    store_uuid: Optional[str] = None
    category_uuid: Optional[str] = None
    primary_image_uuid: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    sku: Optional[str] = None
    price: Optional[int] = None
    sale_price: Optional[int] = None
    currency: Optional[str] = None
    is_service: Optional[bool] = None
    is_bookable: Optional[bool] = None
    is_available: Optional[bool] = None
    is_on_sale: Optional[bool] = None
    is_recommended: Optional[bool] = None
    can_pickup: Optional[bool] = None
    status: Optional[str] = None
    meta: Optional[dict] = None
    youtube_urls: Optional[List[str]] = None
    store_uuid: Optional[str] = None
    category_uuid: Optional[str] = None
    primary_image_uuid: Optional[str] = None


class ProductOut(ProductBase):
    uuid: str
    public_id: str
    company_uuid: Optional[str] = None
    store_uuid: Optional[str] = None
    category_uuid: Optional[str] = None
    primary_image_uuid: Optional[str] = None
    slug: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Cart schemas
class CartItemBase(BaseModel):
    """Cart item structure (stored in JSON)."""
    id: str
    store_id: str
    store_location_id: Optional[str] = None
    product_id: str
    product_image_url: Optional[str] = None
    name: str
    description: Optional[str] = None
    quantity: int
    price: int  # in cents
    subtotal: int  # in cents
    variants: Optional[List[dict]] = None
    addons: Optional[List[dict]] = None
    scheduled_at: Optional[str] = None
    meta: Optional[dict] = None


class CartBase(BaseModel):
    currency: Optional[str] = "USD"
    discount_code: Optional[str] = None
    items: Optional[List[dict]] = Field(default_factory=list, description="Cart items as JSON")
    expires_at: Optional[datetime] = None


class CartCreate(CartBase):
    unique_identifier: Optional[str] = None
    customer_id: Optional[str] = None


class CartOut(CartBase):
    uuid: str
    public_id: str
    company_uuid: Optional[str] = None
    user_uuid: Optional[str] = None
    checkout_uuid: Optional[str] = None
    customer_id: Optional[str] = None
    unique_identifier: Optional[str] = None
    events: Optional[List[dict]] = Field(default_factory=list, description="Cart events as JSON")
    total_items: int = Field(default=0, description="Computed: total quantity of items")
    total_unique_items: int = Field(default=0, description="Computed: count of unique items")
    subtotal: int = Field(default=0, description="Computed: subtotal in cents")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AddToCartRequest(BaseModel):
    quantity: int = Field(default=1, ge=1)
    variants: Optional[List[dict]] = Field(default_factory=list)
    addons: Optional[List[dict]] = Field(default_factory=list)
    scheduled_at: Optional[str] = None
    store_location: Optional[str] = None


class UpdateCartItemRequest(BaseModel):
    quantity: Optional[int] = Field(None, ge=1)
    variants: Optional[List[dict]] = None
    addons: Optional[List[dict]] = None
    scheduled_at: Optional[str] = None

