from typing import List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.schedule import Schedule
from app.models.activity import Activity

router = APIRouter(prefix="/int/v1/schedules-monitor", tags=["schedule-monitor"])


@router.get("/tasks", response_model=List[dict])
def get_schedule_monitor_tasks(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Get all scheduled tasks for monitoring."""
    schedules = db.query(Schedule).filter(
        Schedule.company_uuid == current.company_uuid,
        Schedule.deleted_at.is_(None)
    ).all()
    
    tasks = []
    for schedule in schedules:
        # Get last execution from activity log
        last_activity = db.query(Activity).filter(
            Activity.subject_type == "schedule",
            Activity.subject_id == schedule.uuid,
            Activity.log_name == "schedule_execution"
        ).order_by(Activity.created_at.desc()).first()
        
        # Calculate next run (simplified - would need schedule item logic)
        next_run = None
        if schedule.start_date:
            next_run = schedule.start_date.isoformat()
        
        task = {
            "id": schedule.uuid,
            "public_id": schedule.public_id,
            "name": schedule.name,
            "description": schedule.description,
            "status": schedule.status or "active",
            "start_date": schedule.start_date.isoformat() if schedule.start_date else None,
            "end_date": schedule.end_date.isoformat() if schedule.end_date else None,
            "last_execution": last_activity.created_at.isoformat() if last_activity else None,
            "next_run": next_run,
            "created_at": schedule.created_at.isoformat() if schedule.created_at else None,
        }
        tasks.append(task)
    
    return tasks


@router.get("/tasks/{id}/logs", response_model=List[dict])
def get_schedule_monitor_logs(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get execution logs for a specific scheduled task."""
    # Verify schedule exists and belongs to company
    schedule = db.query(Schedule).filter(
        Schedule.company_uuid == current.company_uuid,
        (Schedule.uuid == id) | (Schedule.public_id == id),
        Schedule.deleted_at.is_(None)
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    # Get activity logs for this schedule
    activities = db.query(Activity).filter(
        Activity.subject_type == "schedule",
        Activity.subject_id == schedule.uuid,
        Activity.log_name == "schedule_execution"
    ).order_by(Activity.created_at.desc()).offset(offset).limit(limit).all()
    
    logs = []
    for activity in activities:
        log = {
            "id": activity.uuid,
            "event": activity.event,
            "description": activity.description,
            "properties": activity.properties or {},
            "created_at": activity.created_at.isoformat() if activity.created_at else None,
            "causer_id": activity.causer_id,
            "causer_type": activity.causer_type,
        }
        logs.append(log)
    
    return logs

