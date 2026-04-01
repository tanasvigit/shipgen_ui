from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel


class DashboardWidgetBase(BaseModel):
    dashboard_uuid: str
    name: str
    component: Optional[str] = None
    grid_options: Optional[dict[str, Any]] = None
    options: Optional[dict[str, Any]] = None


class DashboardWidgetCreate(DashboardWidgetBase):
    pass


class DashboardWidgetUpdate(BaseModel):
    dashboard_uuid: Optional[str] = None
    name: Optional[str] = None
    component: Optional[str] = None
    grid_options: Optional[dict[str, Any]] = None
    options: Optional[dict[str, Any]] = None


class DashboardWidgetOut(DashboardWidgetBase):
    id: int
    uuid: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DashboardWidgetResponse(BaseModel):
    dashboard_widget: DashboardWidgetOut


class DashboardWidgetsResponse(BaseModel):
    dashboard_widgets: List[DashboardWidgetOut]
