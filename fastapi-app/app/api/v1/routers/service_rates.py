"""
Service rates endpoints for distance-based pricing.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.service_rate import ServiceRate
from app.models.service_rate_fee import ServiceRateFee
from app.schemas.service_rate import ServiceRateCreate, ServiceRateOut, ServiceRateUpdate
from app.api.v1.routers.auth import _get_current_user
from app.models.user import User

router = APIRouter(prefix="/fleetops/v1/service-rates", tags=["service-rates"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.get("/", response_model=List[ServiceRateOut])
def list_service_rates(
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service_type: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
):
    """List service rates."""
    query = db.query(ServiceRate).filter(ServiceRate.deleted_at.is_(None))
    
    if service_type:
        query = query.filter(ServiceRate.service_type == service_type)
    if currency:
        query = query.filter(ServiceRate.currency.ilike(currency))
    
    service_rates = query.offset(offset).limit(limit).all()
    
    # Load rate_fees relationship
    for rate in service_rates:
        rate.rate_fees = db.query(ServiceRateFee).filter(
            ServiceRateFee.service_rate_uuid == rate.uuid,
            ServiceRateFee.deleted_at.is_(None)
        ).all()
    
    return service_rates


@router.get("/{service_rate_id}", response_model=ServiceRateOut)
def get_service_rate(
    service_rate_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Get a service rate by public_id or uuid."""
    service_rate = db.query(ServiceRate).filter(
        (ServiceRate.public_id == service_rate_id) | (ServiceRate.uuid == service_rate_id),
        ServiceRate.deleted_at.is_(None)
    ).first()
    
    if not service_rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service rate not found."
        )
    
    # Load rate_fees
    service_rate.rate_fees = db.query(ServiceRateFee).filter(
        ServiceRateFee.service_rate_uuid == service_rate.uuid,
        ServiceRateFee.deleted_at.is_(None)
    ).all()
    
    return service_rate


@router.post("/", response_model=ServiceRateOut, status_code=status.HTTP_201_CREATED)
def create_service_rate(
    payload: ServiceRateCreate,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Create a new service rate."""
    service_rate_uuid = str(uuid.uuid4())
    public_id = f"service_{uuid.uuid4().hex[:12]}"
    
    service_rate = ServiceRate(
        uuid=service_rate_uuid,
        public_id=public_id,
        service_name=payload.service_name,
        service_type=payload.service_type,
        base_fee=payload.base_fee,
        per_meter_flat_rate_fee=payload.per_meter_flat_rate_fee,
        per_meter_unit=payload.per_meter_unit,
        rate_calculation_method=payload.rate_calculation_method,
        has_cod_fee=payload.has_cod_fee,
        cod_calculation_method=payload.cod_calculation_method,
        cod_flat_fee=payload.cod_flat_fee,
        cod_percent=payload.cod_percent,
        has_peak_hours_fee=payload.has_peak_hours_fee,
        peak_hours_calculation_method=payload.peak_hours_calculation_method,
        peak_hours_flat_fee=payload.peak_hours_flat_fee,
        peak_hours_percent=payload.peak_hours_percent,
        peak_hours_start=payload.peak_hours_start,
        peak_hours_end=payload.peak_hours_end,
        max_distance=payload.max_distance,
        max_distance_unit=payload.max_distance_unit,
        currency=payload.currency,
        duration_terms=payload.duration_terms,
        estimated_days=payload.estimated_days,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    db.add(service_rate)
    db.flush()
    
    # Create rate fees if provided
    if payload.rate_fees:
        for fee_data in payload.rate_fees:
            fee_uuid = str(uuid.uuid4())
            fee = ServiceRateFee(
                uuid=fee_uuid,
                service_rate_uuid=service_rate.uuid,
                distance=fee_data.distance,
                distance_unit=fee_data.distance_unit,
                min=fee_data.min,
                max=fee_data.max,
                unit=fee_data.unit,
                fee=fee_data.fee,
                currency=fee_data.currency or service_rate.currency,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(fee)
    
    db.commit()
    db.refresh(service_rate)
    
    # Load rate_fees
    service_rate.rate_fees = db.query(ServiceRateFee).filter(
        ServiceRateFee.service_rate_uuid == service_rate.uuid,
        ServiceRateFee.deleted_at.is_(None)
    ).all()
    
    return service_rate


@router.put("/{service_rate_id}", response_model=ServiceRateOut)
def update_service_rate(
    service_rate_id: str,
    payload: ServiceRateUpdate,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Update a service rate."""
    service_rate = db.query(ServiceRate).filter(
        (ServiceRate.public_id == service_rate_id) | (ServiceRate.uuid == service_rate_id),
        ServiceRate.deleted_at.is_(None)
    ).first()
    
    if not service_rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service rate not found."
        )
    
    # Update fields
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service_rate, field, value)
    
    service_rate.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(service_rate)
    
    # Load rate_fees
    service_rate.rate_fees = db.query(ServiceRateFee).filter(
        ServiceRateFee.service_rate_uuid == service_rate.uuid,
        ServiceRateFee.deleted_at.is_(None)
    ).all()
    
    return service_rate


@router.delete("/{service_rate_id}", status_code=status.HTTP_200_OK)
def delete_service_rate(
    service_rate_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Soft delete a service rate."""
    service_rate = db.query(ServiceRate).filter(
        (ServiceRate.public_id == service_rate_id) | (ServiceRate.uuid == service_rate_id),
        ServiceRate.deleted_at.is_(None)
    ).first()
    
    if not service_rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service rate not found."
        )
    
    service_rate.deleted_at = datetime.now(timezone.utc)
    db.commit()
    
    return {"message": "Service rate deleted successfully."}

