"""
Pydantic schemas for service quotes.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ServiceQuoteItemBase(BaseModel):
    amount: int = Field(..., description="Amount in cents")
    currency: Optional[str] = "USD"
    details: Optional[str] = None
    code: Optional[str] = Field(None, description="'BASE_FEE', 'SERVICE_FEE', 'COD_FEE', etc.")


class ServiceQuoteItemCreate(ServiceQuoteItemBase):
    pass


class ServiceQuoteItemOut(ServiceQuoteItemBase):
    uuid: str
    service_quote_uuid: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ServiceQuoteBase(BaseModel):
    amount: int = Field(..., description="Total amount in cents")
    currency: Optional[str] = "USD"
    meta: Optional[dict] = None
    expired_at: Optional[datetime] = None


class ServiceQuoteCreate(ServiceQuoteBase):
    service_rate_uuid: Optional[str] = None
    request_id: Optional[str] = None
    items: Optional[List[ServiceQuoteItemCreate]] = []


class ServiceQuoteOut(ServiceQuoteBase):
    uuid: str
    public_id: str
    request_id: Optional[str] = None
    company_uuid: Optional[str] = None
    service_rate_uuid: Optional[str] = None
    items: List[ServiceQuoteItemOut] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Request schemas for quote generation
class QuoteFromCartRequest(BaseModel):
    origin: dict = Field(..., description="Origin location with latitude/longitude or place data")
    destination: dict = Field(..., description="Destination location with latitude/longitude or place data")
    service_type: Optional[str] = Field(None, description="Service type filter")
    currency: Optional[str] = Field(None, description="Currency filter")
    is_cash_on_delivery: bool = Field(default=False, description="Whether COD fee should be applied")
    distance: Optional[int] = Field(None, description="Distance in meters (if pre-calculated)")
    time: Optional[int] = Field(None, description="Time in seconds (if pre-calculated)")

