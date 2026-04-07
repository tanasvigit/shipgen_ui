"""Multi-tenant helpers for fleetops resources scoped by user.company_uuid."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.models.user import User


def require_company_uuid(current: User) -> str:
    """Return the current user's company UUID or raise 400."""
    cid = getattr(current, "company_uuid", None)
    if not cid or not str(cid).strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user is not associated with a company.",
        )
    return str(cid)
