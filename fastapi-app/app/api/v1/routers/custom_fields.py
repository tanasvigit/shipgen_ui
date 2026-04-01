import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.custom_field import CustomField
from app.models.user import User

router = APIRouter(prefix="/int/v1/custom-fields", tags=["custom-fields"])


def _serialize_field(field: CustomField) -> dict:
    """Convert CustomField model to plain dict."""
    data = field.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


class CustomFieldCreate(BaseModel):
    name: str
    label: Optional[str] = None
    type: Optional[str] = None
    for_field: Optional[str] = None
    component: Optional[str] = None
    options: Optional[dict] = None
    required: Optional[bool] = False
    editable: Optional[bool] = True
    default_value: Optional[str] = None
    validation_rules: Optional[dict] = None
    category_uuid: Optional[str] = None
    subject_uuid: Optional[str] = None
    subject_type: Optional[str] = None
    description: Optional[str] = None
    help_text: Optional[str] = None
    order: Optional[int] = None


@router.get("/", response_model=List[dict])
def list_custom_fields(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    subject_type: Optional[str] = None,
    subject_uuid: Optional[str] = None,
):
    query = db.query(CustomField).filter(
        CustomField.company_uuid == current.company_uuid,
        CustomField.deleted_at.is_(None)
    )
    if subject_type:
        query = query.filter(CustomField.subject_type == subject_type)
    if subject_uuid:
        query = query.filter(CustomField.subject_uuid == subject_uuid)
    
    fields = (
        query.order_by(CustomField.order.asc().nullslast())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_serialize_field(f) for f in fields]


@router.get("/{id}", response_model=dict)
def get_custom_field(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = db.query(CustomField).filter(
        CustomField.company_uuid == current.company_uuid,
        CustomField.deleted_at.is_(None),
    )
    field = base_query.filter(CustomField.uuid == id).first()
    if not field:
        try:
            numeric_id = int(id)
        except ValueError:
            numeric_id = None
        if numeric_id is not None:
            field = base_query.filter(CustomField.id == numeric_id).first()
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom field not found")
    return _serialize_field(field)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_custom_field(
    payload: CustomFieldCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    field = CustomField()
    field.uuid = str(uuid.uuid4())
    field.company_uuid = current.company_uuid
    field.name = payload.name
    field.label = payload.label or payload.name
    field.type = payload.type
    field.for_field = payload.for_field
    field.component = payload.component
    field.options = payload.options or {}
    field.required = payload.required
    field.editable = payload.editable
    field.default_value = payload.default_value
    field.validation_rules = payload.validation_rules or {}
    field.category_uuid = payload.category_uuid
    field.subject_uuid = payload.subject_uuid
    field.subject_type = payload.subject_type
    field.description = payload.description
    field.help_text = payload.help_text
    field.order = payload.order
    field.created_at = datetime.now(timezone.utc)
    field.updated_at = datetime.now(timezone.utc)

    db.add(field)
    db.commit()
    db.refresh(field)
    return _serialize_field(field)


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_custom_field(
    id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = db.query(CustomField).filter(
        CustomField.company_uuid == current.company_uuid,
        CustomField.deleted_at.is_(None),
    )
    field = base_query.filter(CustomField.uuid == id).first()
    if not field:
        try:
            numeric_id = int(id)
        except ValueError:
            numeric_id = None
        if numeric_id is not None:
            field = base_query.filter(CustomField.id == numeric_id).first()
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom field not found")
    
    for field_name, value in payload.items():
        if hasattr(field, field_name):
            setattr(field, field_name, value)
    
    field.updated_at = datetime.now(timezone.utc)
    db.add(field)
    db.commit()
    db.refresh(field)
    return _serialize_field(field)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_custom_field(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = db.query(CustomField).filter(
        CustomField.company_uuid == current.company_uuid,
        CustomField.deleted_at.is_(None),
    )
    field = base_query.filter(CustomField.uuid == id).first()
    if not field:
        try:
            numeric_id = int(id)
        except ValueError:
            numeric_id = None
        if numeric_id is not None:
            field = base_query.filter(CustomField.id == numeric_id).first()
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom field not found")
    
    field.deleted_at = datetime.now(timezone.utc)
    db.add(field)
    db.commit()
    return {"status": "ok", "message": "Custom field deleted"}

