from typing import List
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.issue import Issue
from app.models.driver import Driver
from app.models.user import User
from app.schemas.issue import IssueCreate, IssueOut, IssueUpdate, IssueResponse, IssuesResponse

router = APIRouter(prefix="/fleetops/v1/issues", tags=["fleetops-issues"])


@router.get("/", response_model=IssuesResponse)
def list_issues(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    q = db.query(Issue).filter(Issue.company_uuid == current.company_uuid, Issue.deleted_at.is_(None))
    issues = q.offset(offset).limit(limit).all()
    return {"issues": issues}


@router.get("/{id}", response_model=IssueResponse)
def get_issue(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    issue = (
        db.query(Issue)
        .filter(Issue.company_uuid == current.company_uuid, (Issue.uuid == id) | (Issue.public_id == id))
        .first()
    )
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found.")
    return {"issue": issue}


@router.post("/", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
def create_issue(
    payload: IssueCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Find driver if provided
    driver = None
    if payload.driver:
        driver = (
            db.query(Driver)
            .filter(Driver.company_uuid == current.company_uuid, (Driver.uuid == payload.driver) | (Driver.public_id == payload.driver))
            .first()
        )
        if not driver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver reporting issue not found.")

    issue = Issue()
    issue.uuid = str(uuid.uuid4())
    issue.public_id = f"issue_{uuid.uuid4().hex[:12]}"
    issue.company_uuid = current.company_uuid
    issue.driver_uuid = driver.uuid if driver else None
    issue.vehicle_uuid = driver.vehicle_uuid if driver else None
    issue.reported_by_uuid = driver.user_uuid if driver else current.uuid
    issue.category = payload.category
    issue.type = payload.type
    issue.report = payload.report
    issue.priority = payload.priority
    issue.status = payload.status or "pending"
    issue.title = payload.title
    issue.tags = payload.tags
    issue.meta = payload.meta

    # Handle location
    if payload.location:
        if isinstance(payload.location, dict):
            issue.latitude = payload.location.get("latitude") or payload.location.get("lat")
            issue.longitude = payload.location.get("longitude") or payload.location.get("lng")
            issue.location_latitude = issue.latitude
            issue.location_longitude = issue.longitude

    db.add(issue)
    db.commit()
    db.refresh(issue)
    return {"issue": issue}


@router.put("/{id}", response_model=IssueResponse)
def update_issue(
    id: str,
    payload: IssueUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    issue = (
        db.query(Issue)
        .filter(Issue.company_uuid == current.company_uuid, (Issue.uuid == id) | (Issue.public_id == id))
        .first()
    )
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found.")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(issue, field, value)

    db.add(issue)
    db.commit()
    db.refresh(issue)
    return {"issue": issue}


@router.delete("/{id}", response_model=IssueResponse)
def delete_issue(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    issue = (
        db.query(Issue)
        .filter(Issue.company_uuid == current.company_uuid, (Issue.uuid == id) | (Issue.public_id == id))
        .first()
    )
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found.")

    issue.deleted_at = datetime.utcnow()
    db.add(issue)
    db.commit()
    return {"issue": issue}

