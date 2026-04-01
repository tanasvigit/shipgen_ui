"""
Service quotes endpoints for generating quotes from cart/coordinates.
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.service_rate import ServiceRate
from app.models.service_quote import ServiceQuote, ServiceQuoteItem
from app.schemas.service_quote import (
    ServiceQuoteOut,
    QuoteFromCartRequest,
)
from app.services.pricing import PricingCalculator
from app.api.v1.routers.auth import _get_current_user
from app.models.user import User

router = APIRouter(prefix="/fleetops/v1/service-quotes", tags=["service-quotes"])
bearer_scheme = HTTPBearer(auto_error=False)


def _extract_coordinates(location: dict) -> tuple[float, float]:
    """Extract latitude and longitude from location dict."""
    # Support multiple formats
    if "latitude" in location and "longitude" in location:
        return float(location["latitude"]), float(location["longitude"])
    elif "lat" in location and "lng" in location:
        return float(location["lat"]), float(location["lng"])
    elif "lat" in location and "lon" in location:
        return float(location["lat"]), float(location["lon"])
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location must contain latitude/longitude or lat/lng"
        )


@router.post("/from-cart", response_model=ServiceQuoteOut, status_code=status.HTTP_201_CREATED)
def create_quote_from_cart(
    payload: QuoteFromCartRequest,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
    all_quotes: bool = Query(False, alias="all", description="Return all quotes instead of best"),
):
    """
    Generate a service quote from cart/coordinates.
    
    This endpoint calculates a quote based on:
    - Origin and destination coordinates
    - Distance-based service rates
    - Optional COD and peak hours fees
    """
    try:
        # Extract coordinates
        origin_lat, origin_lng = _extract_coordinates(payload.origin)
        dest_lat, dest_lng = _extract_coordinates(payload.destination)
        
        # Calculate distance if not provided
        total_distance = payload.distance
        if total_distance is None:
            total_distance = PricingCalculator.calculate_distance_meters(
                origin_lat, origin_lng, dest_lat, dest_lng
            )
        
        total_time = payload.time or 0
        
        # Find applicable service rates
        query = db.query(ServiceRate).filter(
            ServiceRate.deleted_at.is_(None)
        )
        
        if payload.service_type:
            query = query.filter(ServiceRate.service_type == payload.service_type)
        if payload.currency:
            query = query.filter(ServiceRate.currency.ilike(payload.currency))
        
        service_rates = query.all()
        
        if not service_rates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No service rates found matching criteria."
            )
        
        # Load rate_fees for each service rate
        for rate in service_rates:
            rate.rate_fees = db.query(ServiceRateFee).filter(
                ServiceRateFee.service_rate_uuid == rate.uuid,
                ServiceRateFee.deleted_at.is_(None)
            ).all()
        
        # Generate quotes for each service rate
        request_id = f"request_{uuid.uuid4().hex[:12]}"
        quotes = []
        
        for service_rate in service_rates:
            # Calculate quote
            subtotal, lines = PricingCalculator.calculate_quote_from_preliminary(
                service_rate=service_rate,
                total_distance=total_distance,
                total_time=total_time,
                is_cash_on_delivery=payload.is_cash_on_delivery,
            )
            
            # Create service quote
            quote_uuid = str(uuid.uuid4())
            public_id = f"quote_{uuid.uuid4().hex[:12]}"
            
            quote = ServiceQuote(
                uuid=quote_uuid,
                public_id=public_id,
                request_id=request_id,
                service_rate_uuid=service_rate.uuid,
                amount=subtotal,
                currency=service_rate.currency or "USD",
                meta={
                    "origin": payload.origin,
                    "destination": payload.destination,
                    "distance": total_distance,
                    "time": total_time,
                },
                expired_at=datetime.now(timezone.utc) + timedelta(hours=24),  # 24 hour expiry
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            
            db.add(quote)
            db.flush()
            
            # Create quote items
            for line in lines:
                item_uuid = str(uuid.uuid4())
                item = ServiceQuoteItem(
                    uuid=item_uuid,
                    service_quote_uuid=quote.uuid,
                    amount=line["amount"],
                    currency=line["currency"],
                    details=line["details"],
                    code=line["code"],
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                db.add(item)
            
            db.flush()
            quote.items = db.query(ServiceQuoteItem).filter(
                ServiceQuoteItem.service_quote_uuid == quote.uuid
            ).all()
            
            quotes.append(quote)
        
        db.commit()
        
        # If all_quotes is False, return the best (cheapest) quote
        if not all_quotes:
            best_quote = min(quotes, key=lambda q: q.amount or 0)
            # Refresh to get items
            db.refresh(best_quote)
            best_quote.items = db.query(ServiceQuoteItem).filter(
                ServiceQuoteItem.service_quote_uuid == best_quote.uuid
            ).all()
            return best_quote
        
        # Return all quotes (for now, just return first one as list)
        # In a full implementation, you'd return a collection
        return quotes[0] if quotes else None
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating quote: {str(e)}"
        )


@router.get("/{quote_id}", response_model=ServiceQuoteOut)
def get_service_quote(
    quote_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Get a service quote by public_id or uuid."""
    quote = db.query(ServiceQuote).filter(
        (ServiceQuote.public_id == quote_id) | (ServiceQuote.uuid == quote_id),
        ServiceQuote.deleted_at.is_(None)
    ).first()
    
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service quote not found."
        )
    
    # Load items
    quote.items = db.query(ServiceQuoteItem).filter(
        ServiceQuoteItem.service_quote_uuid == quote.uuid,
        ServiceQuoteItem.deleted_at.is_(None)
    ).all()
    
    return quote


@router.get("/", response_model=List[ServiceQuoteOut])
def list_service_quotes(
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    request_id: Optional[str] = Query(None),
):
    """List service quotes."""
    query = db.query(ServiceQuote).filter(ServiceQuote.deleted_at.is_(None))
    
    if request_id:
        query = query.filter(ServiceQuote.request_id == request_id)
    
    quotes = query.offset(offset).limit(limit).all()
    
    # Load items for each quote
    for quote in quotes:
        quote.items = db.query(ServiceQuoteItem).filter(
            ServiceQuoteItem.service_quote_uuid == quote.uuid,
            ServiceQuoteItem.deleted_at.is_(None)
        ).all()
    
    return quotes

