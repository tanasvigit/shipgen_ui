from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RoleBase(BaseModel):
    id: Optional[str] = None
    name: str
    guard_name: str = "sanctum"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RoleCreate(BaseModel):
    name: str
    guard_name: str = "sanctum"


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    guard_name: Optional[str] = None


class RoleOut(RoleBase):
    class Config:
        from_attributes = True


class PermissionBase(BaseModel):
    id: Optional[str] = None
    name: str
    guard_name: str = "sanctum"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PermissionCreate(BaseModel):
    name: str
    guard_name: str = "sanctum"


class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    guard_name: Optional[str] = None


class PermissionOut(PermissionBase):
    class Config:
        from_attributes = True


class PolicyBase(BaseModel):
    id: Optional[str] = None
    company_uuid: Optional[str] = None
    name: str
    guard_name: str = "sanctum"
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PolicyCreate(BaseModel):
    company_uuid: Optional[str] = None
    name: str
    guard_name: str = "sanctum"
    description: Optional[str] = None


class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    guard_name: Optional[str] = None
    description: Optional[str] = None


class PolicyOut(PolicyBase):
    class Config:
        from_attributes = True



