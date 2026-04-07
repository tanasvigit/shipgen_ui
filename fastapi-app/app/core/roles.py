"""Fixed logistics RBAC role names and helpers."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status

from app.models.user import User

ADMIN = "ADMIN"
OPERATIONS_MANAGER = "OPERATIONS_MANAGER"
DISPATCHER = "DISPATCHER"
DRIVER = "DRIVER"
VIEWER = "VIEWER"

ALL_ROLES: frozenset[str] = frozenset({ADMIN, OPERATIONS_MANAGER, DISPATCHER, DRIVER, VIEWER})

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
