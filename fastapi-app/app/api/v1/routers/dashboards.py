from typing import List, Optional, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.dashboard import Dashboard
from app.models.user import User

router = APIRouter(prefix="/int/v1/dashboards", tags=["dashboards"])


from typing import List, Optional, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.dashboard import Dashboard
from app.models.user import User
from app.schemas.dashboard import (
    DashboardCreate,
    DashboardUpdate,
    DashboardOut,
    DashboardResponse,
    DashboardsResponse,
)

router = APIRouter(prefix="/int/v1/dashboards", tags=["dashboards"])


@router.get("/", response_model=DashboardsResponse)
def list_dashboards(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    # Ember passes limit=-1 to mean "no limit"
    limit: int = Query(-1, ge=-1),
    offset: int = Query(0, ge=0),
):
    query = db.query(Dashboard).filter(
        Dashboard.user_uuid == current.uuid,
        Dashboard.company_uuid == current.company_uuid,
        Dashboard.deleted_at.is_(None),
    ).offset(offset)

    if limit != -1:
        query = query.limit(limit)

    dashboards = query.all()

    return {"dashboards": [DashboardOut.from_orm(d) for d in dashboards]}


@router.get("/{id}", response_model=DashboardResponse)
def get_dashboard(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    dashboard = db.query(Dashboard).filter(
        Dashboard.company_uuid == current.company_uuid,
        (Dashboard.uuid == id) | (Dashboard.id == int(id) if id.isdigit() else False),
        Dashboard.deleted_at.is_(None)
    ).first()
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
    
    return {"dashboard": DashboardOut.from_orm(dashboard)}


@router.post("/", response_model=DashboardResponse, status_code=status.HTTP_201_CREATED)
def create_dashboard(
    payload: DashboardCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # If this is set as default, unset other defaults for this user
    if payload.is_default:
        db.query(Dashboard).filter(
            Dashboard.user_uuid == current.uuid,
            Dashboard.company_uuid == current.company_uuid
        ).update({"is_default": False})
    
    dashboard = Dashboard()
    dashboard.uuid = str(uuid.uuid4())
    dashboard.user_uuid = current.uuid
    dashboard.company_uuid = current.company_uuid
    dashboard.name = payload.name
    dashboard.extension = payload.extension
    dashboard.is_default = payload.is_default
    dashboard.tags = payload.tags
    dashboard.meta = payload.meta
    dashboard.options = payload.options
    dashboard.created_at = datetime.utcnow()
    dashboard.updated_at = datetime.utcnow()
    
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    
    return {"dashboard": DashboardOut.from_orm(dashboard)}


@router.put("/{id}", response_model=DashboardResponse)
@router.patch("/{id}", response_model=DashboardResponse)
def update_dashboard(
    id: str,
    payload: DashboardUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    dashboard = db.query(Dashboard).filter(
        Dashboard.company_uuid == current.company_uuid,
        (Dashboard.uuid == id) | (Dashboard.id == int(id) if id.isdigit() else False),
        Dashboard.deleted_at.is_(None)
    ).first()
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
    
    # If setting as default, unset other defaults
    if payload.is_default is True:
        db.query(Dashboard).filter(
            Dashboard.user_uuid == current.uuid,
            Dashboard.company_uuid == current.company_uuid,
            Dashboard.uuid != dashboard.uuid
        ).update({"is_default": False})
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(dashboard, field):
            setattr(dashboard, field, value)
    
    dashboard.updated_at = datetime.utcnow()
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    
    return {"dashboard": DashboardOut.from_orm(dashboard)}


@router.delete("/{id}", response_model=DashboardResponse)
def delete_dashboard(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    dashboard = db.query(Dashboard).filter(
        Dashboard.company_uuid == current.company_uuid,
        (Dashboard.uuid == id) | (Dashboard.id == int(id) if id.isdigit() else False),
        Dashboard.deleted_at.is_(None)
    ).first()
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
    
    dashboard.deleted_at = datetime.utcnow()
    db.add(dashboard)
    db.commit()
    
    return {"dashboard": DashboardOut.from_orm(dashboard)}


@router.post("/switch", response_model=DashboardResponse)
def switch_dashboard(
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    dashboard_id = payload.get("dashboard_uuid") or payload.get("dashboard")
    if not dashboard_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dashboard ID required")

    dashboard = db.query(Dashboard).filter(
        Dashboard.user_uuid == current.uuid,
        (Dashboard.uuid == dashboard_id) | (Dashboard.id == int(dashboard_id) if str(dashboard_id).isdigit() else False),
        Dashboard.deleted_at.is_(None)
    ).first()
    
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
    
    # Unset all defaults for this user
    db.query(Dashboard).filter(
        Dashboard.user_uuid == current.uuid,
        Dashboard.company_uuid == current.company_uuid
    ).update({"is_default": False})
    
    # Set this as default
    dashboard.is_default = True
    dashboard.updated_at = datetime.utcnow()
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    
    return {"dashboard": DashboardOut.from_orm(dashboard)}


@router.post("/reset-default", response_model=dict)
def reset_default_dashboard(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Unset all defaults for this user
    db.query(Dashboard).filter(
        Dashboard.user_uuid == current.uuid,
        Dashboard.company_uuid == current.company_uuid
    ).update({"is_default": False})
    db.commit()
    
    return {"status": "ok"}

