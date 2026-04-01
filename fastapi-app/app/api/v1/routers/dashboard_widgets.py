from typing import List, Optional, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.dashboard_widget import DashboardWidget
from app.models.user import User

router = APIRouter(prefix="/int/v1/dashboard-widgets", tags=["dashboard-widgets"])


from typing import List, Optional, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.dashboard_widget import DashboardWidget
from app.models.user import User
from app.schemas.dashboard_widget import (
    DashboardWidgetCreate,
    DashboardWidgetUpdate,
    DashboardWidgetOut,
    DashboardWidgetResponse,
    DashboardWidgetsResponse,
)

router = APIRouter(prefix="/int/v1/dashboard-widgets", tags=["dashboard-widgets"])


@router.get("/", response_model=DashboardWidgetsResponse)
def list_dashboard_widgets(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    dashboard_uuid: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(DashboardWidget).filter(
        DashboardWidget.deleted_at.is_(None)
    )
    
    if dashboard_uuid:
        query = query.filter(DashboardWidget.dashboard_uuid == dashboard_uuid)
    
    widgets = query.offset(offset).limit(limit).all()
    return {"dashboard_widgets": [DashboardWidgetOut.from_orm(w) for w in widgets]}


@router.get("/{id}", response_model=DashboardWidgetResponse)
def get_dashboard_widget(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    widget = db.query(DashboardWidget).filter(
        (DashboardWidget.uuid == id) | (DashboardWidget.id == int(id) if id.isdigit() else False),
        DashboardWidget.deleted_at.is_(None)
    ).first()
    if not widget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard widget not found")
    
    return {"dashboard_widget": DashboardWidgetOut.from_orm(widget)}


@router.post("/", response_model=DashboardWidgetResponse, status_code=status.HTTP_201_CREATED)
def create_dashboard_widget(
    payload: DashboardWidgetCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    widget = DashboardWidget()
    widget.uuid = str(uuid.uuid4())
    widget.dashboard_uuid = payload.dashboard_uuid
    widget.name = payload.name
    widget.component = payload.component
    widget.grid_options = payload.grid_options
    widget.options = payload.options
    widget.created_at = datetime.utcnow()
    widget.updated_at = datetime.utcnow()
    
    db.add(widget)
    db.commit()
    db.refresh(widget)
    
    return {"dashboard_widget": DashboardWidgetOut.from_orm(widget)}


@router.put("/{id}", response_model=DashboardWidgetResponse)
@router.patch("/{id}", response_model=DashboardWidgetResponse)
def update_dashboard_widget(
    id: str,
    payload: DashboardWidgetUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    widget = db.query(DashboardWidget).filter(
        (DashboardWidget.uuid == id) | (DashboardWidget.id == int(id) if id.isdigit() else False),
        DashboardWidget.deleted_at.is_(None)
    ).first()
    if not widget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard widget not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(widget, field):
            setattr(widget, field, value)
    
    widget.updated_at = datetime.utcnow()
    db.add(widget)
    db.commit()
    db.refresh(widget)
    
    return {"dashboard_widget": DashboardWidgetOut.from_orm(widget)}


@router.delete("/{id}", response_model=DashboardWidgetResponse)
def delete_dashboard_widget(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    widget = db.query(DashboardWidget).filter(
        (DashboardWidget.uuid == id) | (DashboardWidget.id == int(id) if id.isdigit() else False),
        DashboardWidget.deleted_at.is_(None)
    ).first()
    if not widget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard widget not found")
    
    widget.deleted_at = datetime.utcnow()
    db.add(widget)
    db.commit()
    
    return {"dashboard_widget": DashboardWidgetOut.from_orm(widget)}

