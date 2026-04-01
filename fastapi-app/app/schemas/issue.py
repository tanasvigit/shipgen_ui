from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class IssueBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    issue_id: Optional[str] = None
    company_uuid: Optional[str] = None
    driver_uuid: Optional[str] = None
    vehicle_uuid: Optional[str] = None
    assigned_to_uuid: Optional[str] = None
    reported_by_uuid: Optional[str] = None
    location: Optional[dict[str, Any]] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    report: Optional[str] = None
    title: Optional[str] = None
    tags: Optional[list[str]] = None
    priority: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    resolved_at: Optional[datetime] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IssueCreate(BaseModel):
    driver: Optional[str] = None  # public_id
    location: Optional[dict[str, Any]] = None
    category: Optional[str] = None
    type: Optional[str] = None
    report: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    title: Optional[str] = None
    tags: Optional[list[str]] = None
    meta: Optional[dict[str, Any]] = None


class IssueUpdate(BaseModel):
    category: Optional[str] = None
    type: Optional[str] = None
    report: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    title: Optional[str] = None
    tags: Optional[list[str]] = None
    meta: Optional[dict[str, Any]] = None
    resolved_at: Optional[datetime] = None




class IssueOut(IssueBase):
    id: Optional[int] = None
    driver_name: Optional[str] = None
    vehicle_name: Optional[str] = None
    assignee_name: Optional[str] = None
    reporter_name: Optional[str] = None

    class Config:
        from_attributes = True


class IssueResponse(BaseModel):
    issue: IssueOut


class IssuesResponse(BaseModel):
    issues: List[IssueOut]

