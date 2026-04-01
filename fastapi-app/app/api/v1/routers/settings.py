from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.setting import Setting
from app.models.user import User

router = APIRouter(prefix="/int/v1/settings", tags=["settings"])


class SettingCreate(BaseModel):
    key: str
    value: Any


class SettingUpdate(BaseModel):
    value: Any


@router.get("/", response_model=List[dict])
def list_settings(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    settings = db.query(Setting).offset(offset).limit(limit).all()
    return [s.__dict__ for s in settings]


@router.get("/branding", response_model=dict)
def get_branding_settings(
    db: Session = Depends(get_db),
):
    """Get branding settings for the company. No authentication required. Must be defined before /{key} route."""
    branding_keys = [
        "branding.icon_url",
        "branding.logo_url",
        "branding.default_theme",
        "branding.primary_color",
        "branding.secondary_color",
        "branding.company_name",
    ]
    
    settings_dict = {}
    for key in branding_keys:
        setting = db.query(Setting).filter(Setting.key == key).first()
        if setting:
            settings_dict[key.replace("branding.", "")] = setting.value
    
    # Get defaults. The Ember console expects this to behave like a
    # single `brand` record, so we include a stable `id`/`uuid` field.
    return {
        "id": "1",
        "uuid": "1",
        "icon_url": settings_dict.get("icon_url"),
        "logo_url": settings_dict.get("logo_url"),
        "default_theme": settings_dict.get("default_theme", "dark"),
        "primary_color": settings_dict.get("primary_color", "#007bff"),
        "secondary_color": settings_dict.get("secondary_color", "#6c757d"),
        "company_name": settings_dict.get("company_name"),
        # Optional UUIDs for uploaded assets; console will treat null as unset.
        "logo_uuid": None,
        "icon_uuid": None,
    }


@router.get("/{key}", response_model=dict)
def get_setting(
    key: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    return setting.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_setting(
    payload: SettingCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Check if setting already exists
    existing = db.query(Setting).filter(Setting.key == payload.key).first()
    if existing:
        existing.value = payload.value
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing.__dict__
    
    setting = Setting()
    setting.key = payload.key
    setting.value = payload.value
    
    db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting.__dict__


@router.put("/{key}", response_model=dict)
def update_setting(
    key: str,
    payload: SettingUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    
    setting.value = payload.value
    db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting.__dict__


@router.post("/branding", response_model=dict)
@router.put("/branding", response_model=dict)
def save_branding_settings(
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Save branding settings for the company."""
    branding_keys = {
        "icon_url": "branding.icon_url",
        "logo_url": "branding.logo_url",
        "default_theme": "branding.default_theme",
        "primary_color": "branding.primary_color",
        "secondary_color": "branding.secondary_color",
        "company_name": "branding.company_name",
    }
    
    saved_settings = {}
    
    for key, setting_key in branding_keys.items():
        if key in payload:
            # Check if setting exists
            setting = db.query(Setting).filter(Setting.key == setting_key).first()
            if setting:
                setting.value = payload[key]
                db.add(setting)
            else:
                new_setting = Setting()
                new_setting.key = setting_key
                new_setting.value = payload[key]
                db.add(new_setting)
            saved_settings[key] = payload[key]
    
    db.commit()
    
    return {
        "message": "Branding settings saved",
        "settings": saved_settings
    }

