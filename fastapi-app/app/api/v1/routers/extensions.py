import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.extension import Extension
from app.models.user import User

router = APIRouter(prefix="/int/v1/extensions", tags=["extensions"])


def _serialize_extension(ext: Extension) -> dict:
    """Convert Extension model to plain dict without SQLAlchemy state."""
    data = ext.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


class ExtensionCreate(BaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    category_uuid: Optional[str] = None
    type_uuid: Optional[str] = None
    tags: Optional[List[str]] = None
    namespace: Optional[str] = None
    version: Optional[str] = None
    config: Optional[dict] = None
    meta: Optional[dict] = None


@router.get("/", response_model=List[dict])
def list_extensions(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = None,
    type: Optional[str] = None,
):
    query = db.query(Extension).filter(Extension.deleted_at.is_(None))
    if category:
        query = query.filter(Extension.category_uuid == category)
    if type:
        query = query.filter(Extension.type_uuid == type)
    
    extensions = query.offset(offset).limit(limit).all()
    return [_serialize_extension(e) for e in extensions]


@router.get("/{id}", response_model=dict)
def get_extension(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    extension = (
        db.query(Extension)
        .filter(
            (Extension.uuid == id) | (Extension.public_id == id) | (Extension.slug == id),
            Extension.deleted_at.is_(None),
        )
        .first()
    )
    if not extension:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extension not found")
    return _serialize_extension(extension)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_extension(
    payload: ExtensionCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    extension = Extension()
    extension.uuid = str(uuid.uuid4())
    extension.name = payload.name
    extension.display_name = payload.display_name or payload.name
    extension.description = payload.description
    extension.category_uuid = payload.category_uuid
    extension.type_uuid = payload.type_uuid
    extension.tags = payload.tags or []
    extension.namespace = payload.namespace
    extension.version = payload.version
    extension.config = payload.config or {}
    extension.meta = payload.meta or {}
    extension.status = "active"
    extension.created_at = datetime.now(timezone.utc)
    extension.updated_at = datetime.now(timezone.utc)

    db.add(extension)
    db.commit()
    db.refresh(extension)
    return _serialize_extension(extension)


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_extension(
    id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    extension = (
        db.query(Extension)
        .filter(
            (Extension.uuid == id) | (Extension.public_id == id),
            Extension.deleted_at.is_(None),
        )
        .first()
    )
    if not extension:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extension not found")
    
    for field, value in payload.items():
        if hasattr(extension, field):
            setattr(extension, field, value)
    
    extension.updated_at = datetime.now(timezone.utc)
    db.add(extension)
    db.commit()
    db.refresh(extension)
    return _serialize_extension(extension)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_extension(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    extension = db.query(Extension).filter(
        (Extension.uuid == id) | (Extension.public_id == id),
        Extension.deleted_at.is_(None)
    ).first()
    if not extension:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extension not found")
    
    extension.deleted_at = datetime.now(timezone.utc)
    db.add(extension)
    db.commit()
    return {"status": "ok", "message": "Extension deleted"}

