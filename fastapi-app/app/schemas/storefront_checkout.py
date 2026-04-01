from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class CheckoutBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    token: Optional[str] = None
    amount: Optional[int] = None
    currency: Optional[str] = None
    is_cod: Optional[bool] = False
    is_pickup: Optional[bool] = False
    captured: Optional[bool] = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CheckoutInitialize(BaseModel):
    gateway: Optional[str] = None
    customer: Optional[str] = None
    cart: Optional[str] = None
    serviceQuote: Optional[str] = None
    service_quote: Optional[str] = None
    cash: Optional[bool] = False
    pickup: Optional[bool] = False
    tip: Optional[Any] = None
    deliveryTip: Optional[Any] = None
    delivery_tip: Optional[Any] = None


class CheckoutStatusRequest(BaseModel):
    checkout: str
    token: str


class CheckoutCapture(BaseModel):
    token: str
    transactionDetails: Optional[dict[str, Any]] = None
    notes: Optional[str] = None


class CheckoutOut(CheckoutBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True

