"""Fixed logistics RBAC role names and helpers.

Roles:
- ADMIN: Full access including user management
- OPERATIONS_MANAGER: Operations without user admin
- DISPATCHER: Order management and dispatch
- DRIVER: Assigned orders only
- VIEWER: Internal read-only access (NOT external customers)

Note: VIEWER is an internal role for stakeholders who need visibility.
External customers should use the Storefront system.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status

from app.models.user import User

ADMIN = "ADMIN"
OPERATIONS_MANAGER = "OPERATIONS_MANAGER"
DISPATCHER = "DISPATCHER"
DRIVER = "DRIVER"
# VIEWER: Internal read-only role for stakeholders (management, finance, support)
# NOT for external customers - they use Storefront with separate auth
VIEWER = "VIEWER"
FLEET_CUSTOMER = "FLEET_CUSTOMER"

ALL_ROLES: frozenset[str] = frozenset(
    {ADMIN, OPERATIONS_MANAGER, DISPATCHER, DRIVER, VIEWER, FLEET_CUSTOMER}
)

STAFF_ORDER_MUTATORS = frozenset({ADMIN, OPERATIONS_MANAGER, DISPATCHER})


def effective_user_role(user: User) -> str:
    raw = (getattr(user, "role", None) or "").strip().upper()
    if not raw or raw not in ALL_ROLES:
        return DISPATCHER
    return raw


def require_roles(*allowed_roles: str):
    """FastAPI dependency: 403 if current user's role is not in allowed_roles."""
    from app.api.v1.routers.auth import _get_current_user  # noqa: PLC0415

    allowed = frozenset(allowed_roles)

    def _dependency(current: User = Depends(_get_current_user)) -> User:
        if effective_user_role(current) not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current

    return _dependency


def deny_if_viewer(current: User) -> User:
    """
    FastAPI dependency: 403 if current user is VIEWER role.
    
    Use this as an additional guard on mutation endpoints to ensure
    VIEWER (read-only) users cannot perform any modifications.
    
    Example:
        current: User = Depends(deny_if_viewer)
    """
    if effective_user_role(current) == VIEWER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Read-only access: VIEWER role cannot perform mutations"
        )
    return current
