import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.custom_field_value import CustomFieldValue
from app.models.user import User

router = APIRouter(prefix="/int/v1/custom-field-values", tags=["custom-field-values"])


def _serialize_value(val: CustomFieldValue) -> dict:
    """Convert CustomFieldValue model to plain dict."""
    data = val.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


class CustomFieldValueCreate(BaseModel):
    custom_field_uuid: str
    subject_uuid: str
    subject_type: str
    value: Optional[str] = None
    value_type: Optional[str] = None


@router.get("/", response_model=List[dict])
def list_custom_field_values(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    subject_type: Optional[str] = None,
    subject_uuid: Optional[str] = None,
    custom_field_uuid: Optional[str] = None,
):
    query = db.query(CustomFieldValue).filter(
        CustomFieldValue.company_uuid == current.company_uuid,
        CustomFieldValue.deleted_at.is_(None)
    )
    if subject_type:
        query = query.filter(CustomFieldValue.subject_type == subject_type)
    if subject_uuid:
        query = query.filter(CustomFieldValue.subject_uuid == subject_uuid)
    if custom_field_uuid:
        query = query.filter(CustomFieldValue.custom_field_uuid == custom_field_uuid)
    
    values = query.offset(offset).limit(limit).all()
    return [_serialize_value(v) for v in values]


@router.get("/{id}", response_model=dict)
def get_custom_field_value(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = db.query(CustomFieldValue).filter(
        CustomFieldValue.company_uuid == current.company_uuid,
        CustomFieldValue.deleted_at.is_(None),
    )
    value = base_query.filter(CustomFieldValue.uuid == id).first()
    if not value:
        try:
            numeric_id = int(id)
        except ValueError:
            numeric_id = None
        if numeric_id is not None:
            value = base_query.filter(CustomFieldValue.id == numeric_id).first()
    if not value:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom field value not found")
    return _serialize_value(value)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_custom_field_value(
    payload: CustomFieldValueCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    value = CustomFieldValue()
    value.uuid = str(uuid.uuid4())
    value.company_uuid = current.company_uuid
    value.custom_field_uuid = payload.custom_field_uuid
    value.subject_uuid = payload.subject_uuid
    value.subject_type = payload.subject_type
    value.value = payload.value
    value.value_type = payload.value_type
    value.created_at = datetime.now(timezone.utc)
    value.updated_at = datetime.now(timezone.utc)

    db.add(value)
    db.commit()
    db.refresh(value)
    return _serialize_value(value)


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_custom_field_value(
    id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = db.query(CustomFieldValue).filter(
        CustomFieldValue.company_uuid == current.company_uuid,
        CustomFieldValue.deleted_at.is_(None),
    )
    value = base_query.filter(CustomFieldValue.uuid == id).first()
    if not value:
        try:
            numeric_id = int(id)
        except ValueError:
            numeric_id = None
        if numeric_id is not None:
            value = base_query.filter(CustomFieldValue.id == numeric_id).first()
    if not value:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom field value not found")
    
    for field_name, val in payload.items():
        if hasattr(value, field_name):
            setattr(value, field_name, val)
    
    value.updated_at = datetime.now(timezone.utc)
    db.add(value)
    db.commit()
    db.refresh(value)
    return _serialize_value(value)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_custom_field_value(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = db.query(CustomFieldValue).filter(
        CustomFieldValue.company_uuid == current.company_uuid,
        CustomFieldValue.deleted_at.is_(None),
    )
    value = base_query.filter(CustomFieldValue.uuid == id).first()
    if not value:
        try:
            numeric_id = int(id)
        except ValueError:
            numeric_id = None
        if numeric_id is not None:
            value = base_query.filter(CustomFieldValue.id == numeric_id).first()
    if not value:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom field value not found")
    
    value.deleted_at = datetime.now(timezone.utc)
    db.add(value)
    db.commit()
    return {"status": "ok", "message": "Custom field value deleted"}

