from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class GatewayBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    type: Optional[str] = None
    sandbox: Optional[bool] = False
    return_url: Optional[str] = None
    callback_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GatewayOut(GatewayBase):
    id: Optional[int] = None
    logo_url: Optional[str] = None
    is_stripe_gateway: Optional[bool] = None
    is_qpay_gateway: Optional[bool] = None

    class Config:
        from_attributes = True

