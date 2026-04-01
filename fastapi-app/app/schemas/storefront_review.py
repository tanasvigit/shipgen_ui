from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class ReviewBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    created_by_uuid: Optional[str] = None
    customer_uuid: Optional[str] = None
    subject_uuid: Optional[str] = None
    subject_type: Optional[str] = None
    rating: Optional[int] = None
    content: Optional[str] = None
    rejected: Optional[bool] = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ReviewCreate(BaseModel):
    subject: str  # public_id
    rating: int
    content: Optional[str] = None
    files: Optional[list[dict[str, Any]]] = None


class ReviewOut(ReviewBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True

