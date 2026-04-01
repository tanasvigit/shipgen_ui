from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel


class DashboardBase(BaseModel):
    name: str
    extension: Optional[str] = None
    is_default: bool = False
    tags: Optional[List[str]] = None
    meta: Optional[dict[str, Any]] = None
    options: Optional[dict[str, Any]] = None


class DashboardCreate(DashboardBase):
    pass


class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    extension: Optional[str] = None
    is_default: Optional[bool] = None
    tags: Optional[List[str]] = None
    meta: Optional[dict[str, Any]] = None
    options: Optional[dict[str, Any]] = None


class DashboardOut(DashboardBase):
    id: int
    uuid: Optional[str]
    user_uuid: Optional[str]
    company_uuid: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    dashboard: DashboardOut


class DashboardsResponse(BaseModel):
    dashboards: List[DashboardOut]
