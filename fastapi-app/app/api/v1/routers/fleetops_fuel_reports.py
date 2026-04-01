from typing import List
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.fuel_report import FuelReport
from app.models.driver import Driver
from app.models.user import User
from app.schemas.fuel_report import FuelReportCreate, FuelReportOut, FuelReportUpdate, FuelReportResponse, FuelReportsResponse

router = APIRouter(prefix="/fleetops/v1/fuel-reports", tags=["fleetops-fuel-reports"])


@router.get("/", response_model=FuelReportsResponse)
def list_fuel_reports(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    q = db.query(FuelReport).filter(FuelReport.company_uuid == current.company_uuid, FuelReport.deleted_at.is_(None))
    reports = q.offset(offset).limit(limit).all()
    return {"fuel_reports": reports}


@router.get("/{id}", response_model=FuelReportResponse)
def get_fuel_report(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    report = (
        db.query(FuelReport)
        .filter(FuelReport.company_uuid == current.company_uuid, (FuelReport.uuid == id) | (FuelReport.public_id == id))
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fuel report not found.")
    return {"fuel_report": report}


@router.post("/", response_model=FuelReportResponse, status_code=status.HTTP_201_CREATED)
def create_fuel_report(
    payload: FuelReportCreate,
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver reporting fuel report not found.")

    report = FuelReport()
    report.uuid = str(uuid.uuid4())
    report.public_id = f"fuel_report_{uuid.uuid4().hex[:12]}"
    report.company_uuid = current.company_uuid
    report.driver_uuid = driver.uuid if driver else None
    report.vehicle_uuid = driver.vehicle_uuid if driver else None
    report.reported_by_uuid = driver.user_uuid if driver else current.uuid
    report.odometer = payload.odometer
    report.volume = payload.volume
    report.metric_unit = payload.metric_unit
    report.amount = payload.amount
    report.currency = payload.currency
    report.status = payload.status
    report.report = payload.report
    report.meta = payload.meta

    # Handle location
    if payload.location:
        if isinstance(payload.location, dict):
            report.latitude = payload.location.get("latitude") or payload.location.get("lat")
            report.longitude = payload.location.get("longitude") or payload.location.get("lng")
            report.location_latitude = report.latitude
            report.location_longitude = report.longitude

    db.add(report)
    db.commit()
    db.refresh(report)
    return {"fuel_report": report}


@router.put("/{id}", response_model=FuelReportResponse)
def update_fuel_report(
    id: str,
    payload: FuelReportUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    report = (
        db.query(FuelReport)
        .filter(FuelReport.company_uuid == current.company_uuid, (FuelReport.uuid == id) | (FuelReport.public_id == id))
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fuel report not found.")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(report, field, value)

    db.add(report)
    db.commit()
    db.refresh(report)
    return {"fuel_report": report}


@router.delete("/{id}", response_model=FuelReportResponse)
def delete_fuel_report(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    report = (
        db.query(FuelReport)
        .filter(FuelReport.company_uuid == current.company_uuid, (FuelReport.uuid == id) | (FuelReport.public_id == id))
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fuel report not found.")

    report.deleted_at = datetime.utcnow()
    db.add(report)
    db.commit()
    return {"fuel_report": report}

