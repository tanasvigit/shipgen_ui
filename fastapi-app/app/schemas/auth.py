from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Console may send identity or email; we accept both."""
    identity: Optional[str] = None
    email: Optional[str] = None  # alias for identity so frontend can send either
    password: Optional[str] = None
    authToken: Optional[str] = None


class LoginUser(BaseModel):
    """Lightweight user payload returned for login and /me."""
    id: str  # always a non-null string (uuid or cast from int)
    email: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None


class MeUser(BaseModel):
    """User payload for /int/v1/me endpoint expected by Fleetbase console."""
    id: str              # non-null string, typically uuid
    uuid: str            # non-null string, mirrors id/uuid
    email: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    role: Optional[str] = None


class LoginResponse(BaseModel):
    """Response for POST /auth/login."""
    token: Optional[str] = None
    user: Optional[LoginUser] = None
    type: Optional[str] = None
    twoFaSession: Optional[str] = None
    isEnabled: Optional[bool] = None


class SessionData(BaseModel):
    """Console/Ember may expect session or user ref to have a non-null id."""
    id: Optional[str] = None  # Ember; set to user uuid so findRecord('user', id) works
    token: str
    user: str
    verified: bool
    type: Optional[str] = None
    last_modified: Optional[datetime] = None
    impersonator: Optional[Any] = None


class InstallerStatus(BaseModel):
    shouldInstall: bool
    shouldOnboard: bool
    defaultTheme: str = "dark"


class OrganizationSummary(BaseModel):
    """Console/Ember expects each resource to have a non-null id (string or number)."""
    id: Optional[str] = None  # Ember Data; we set to uuid
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None
    status: Optional[str] = None


class OrganizationsResponse(BaseModel):
    """Response for GET /auth/organizations - matches shape expected by console."""
    organizations: list[OrganizationSummary]
    company: Optional[list[OrganizationSummary]] = None


class BootstrapResponse(BaseModel):
    session: SessionData
    organizations: list[OrganizationSummary]
    installer: InstallerStatus



