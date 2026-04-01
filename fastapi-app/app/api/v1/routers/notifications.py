import json
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.company import Company
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import (
    BulkDeleteRequest,
    MarkAsReadRequest,
    NotificationOut,
    NotificationSettings,
)

router = APIRouter(prefix="/int/v1/notifications", tags=["notifications"])


@router.get("/", response_model=List[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    rows = (
        db.query(Notification)
        .filter(Notification.notifiable_type == "user", Notification.notifiable_id == current.uuid)
        .order_by(Notification.created_at.desc().nullslast())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        NotificationOut(
            id=row.id,
            type=row.type,
            notifiable_type=row.notifiable_type,
            notifiable_id=row.notifiable_id,
            data=json.loads(row.data) if row.data else {},
            read_at=row.read_at,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]


@router.put("/mark-as-read")
def mark_as_read(
    payload: MarkAsReadRequest,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    total = len(payload.notifications)
    marked = 0
    now = datetime.now(timezone.utc)

    for notif_id in payload.notifications:
        notif = (
            db.query(Notification)
            .filter(
                Notification.id == notif_id,
                Notification.notifiable_type == "user",
                Notification.notifiable_id == current.uuid,
            )
            .first()
        )
        if notif and notif.read_at is None:
            notif.read_at = now
            db.add(notif)
            marked += 1

    db.commit()

    return {
        "status": "ok",
        "message": "Notifications marked as read",
        "marked_as_read": marked,
        "total": total,
    }


@router.put("/mark-all-read")
def mark_all_read(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    now = datetime.now(timezone.utc)
    rows = (
        db.query(Notification)
        .filter(
            Notification.notifiable_type == "user",
            Notification.notifiable_id == current.uuid,
            Notification.read_at.is_(None),
        )
        .all()
    )
    for row in rows:
        row.read_at = now
        db.add(row)

    db.commit()
    return {"status": "ok", "message": "All notifications marked as read"}


@router.delete("/bulk-delete")
def bulk_delete(
    payload: BulkDeleteRequest,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    q = db.query(Notification).filter(
        Notification.notifiable_type == "user",
        Notification.notifiable_id == current.uuid,
    )
    if payload.notifications:
        q = q.filter(Notification.id.in_(payload.notifications))

    deleted = q.delete(synchronize_session=False)
    db.commit()
    return {"status": "ok", "message": "Selected notifications deleted successfully", "deleted": deleted}


@router.get("/registry")
def registry():
    # Stub: in Laravel this comes from NotificationRegistry
    return []


@router.get("/notifiables")
def notifiables():
    # Stub: in Laravel this comes from NotificationRegistry
    return []


@router.get("/get-settings", response_model=NotificationSettings)
def get_settings(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Simple company-level settings using Company.options JSON
    if not current.company_uuid:
        return NotificationSettings(notificationSettings={})

    company = db.query(Company).filter(Company.uuid == current.company_uuid).first()
    if not company or not company.options:
        return NotificationSettings(notificationSettings={})

    settings = company.options.get("notification_settings") or {}
    return NotificationSettings(notificationSettings=settings)


@router.post("/save-settings")
def save_settings(
    payload: NotificationSettings,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    if not isinstance(payload.notificationSettings, dict):
        raise HTTPException(status_code=400, detail="Invalid notification settings data.")

    if not current.company_uuid:
        raise HTTPException(status_code=400, detail="Current user has no company.")

    company = db.query(Company).filter(Company.uuid == current.company_uuid).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")

    options = company.options or {}
    existing = options.get("notification_settings") or {}
    options["notification_settings"] = {**existing, **payload.notificationSettings}
    company.options = options
    company.updated_at = datetime.now(timezone.utc)
    db.add(company)
    db.commit()

    return {"status": "ok", "message": "Notification settings successfully saved."}



