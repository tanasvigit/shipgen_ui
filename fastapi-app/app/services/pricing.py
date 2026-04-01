"""
Pricing calculation service for distance-based service rates.
"""
from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session

from app.models.service_rate import ServiceRate
from app.models.service_rate_fee import ServiceRateFee
from app.models.service_quote import ServiceQuoteItem


class PricingCalculator:
    """Calculate pricing based on service rate and distance."""
    
    @staticmethod
    def calculate_quote_from_preliminary(
        service_rate: ServiceRate,
        total_distance: int,  # in meters
        total_time: int = 0,  # in seconds
        is_cash_on_delivery: bool = False,
    ) -> Tuple[int, List[dict]]:
        """
        Calculate quote from preliminary data (distance/time).
        
        Returns:
            Tuple of (total_amount_in_cents, list_of_line_items)
        """
        lines: List[dict] = []
        subtotal = service_rate.base_fee or 0
        
        # Add base fee line item
        lines.append({
            "details": "Base Fee",
            "amount": subtotal,
            "currency": service_rate.currency or "USD",
            "code": "BASE_FEE",
        })
        
        # Calculate service fee based on rate calculation method
        if service_rate.is_fixed_meter():
            # Find fee by distance tier
            distance_fee = PricingCalculator._find_fee_by_distance(
                service_rate, total_distance
            )
            if distance_fee:
                fee_amount = distance_fee.fee or 0
                subtotal += fee_amount
                lines.append({
                    "details": "Service Fee",
                    "amount": fee_amount,
                    "currency": service_rate.currency or "USD",
                    "code": "SERVICE_FEE",
                })
        
        elif service_rate.is_per_meter():
            # Calculate per meter fee
            per_meter_distance = total_distance
            if service_rate.per_meter_unit == "km":
                per_meter_distance = round(total_distance / 1000)
            
            rate_fee = per_meter_distance * (service_rate.per_meter_flat_rate_fee or 0)
            subtotal += rate_fee
            lines.append({
                "details": "Service Fee",
                "amount": rate_fee,
                "currency": service_rate.currency or "USD",
                "code": "SERVICE_FEE",
            })
        
        # Store base rate before COD/peak hours
        base_rate = subtotal
        
        # Add COD fee if applicable
        if service_rate.has_cod() and is_cash_on_delivery:
            cod_fee = 0
            if service_rate.cod_calculation_method == "flat":
                cod_fee = service_rate.cod_flat_fee or 0
            elif service_rate.cod_calculation_method == "percentage":
                cod_fee = PricingCalculator._calculate_percentage(
                    service_rate.cod_percent or 0, base_rate
                )
            
            if cod_fee > 0:
                subtotal += cod_fee
                lines.append({
                    "details": "Cash on delivery fee",
                    "amount": cod_fee,
                    "currency": service_rate.currency or "USD",
                    "code": "COD_FEE",
                })
        
        # Add peak hours fee if applicable
        if service_rate.has_peak_hours() and PricingCalculator._is_within_peak_hours(
            service_rate.peak_hours_start, service_rate.peak_hours_end
        ):
            peak_hours_fee = 0
            if service_rate.peak_hours_calculation_method == "flat":
                peak_hours_fee = service_rate.peak_hours_flat_fee or 0
            elif service_rate.peak_hours_calculation_method == "percentage":
                peak_hours_fee = PricingCalculator._calculate_percentage(
                    service_rate.peak_hours_percent or 0, base_rate
                )
            
            if peak_hours_fee > 0:
                subtotal += peak_hours_fee
                lines.append({
                    "details": "Peak hours fee",
                    "amount": peak_hours_fee,
                    "currency": service_rate.currency or "USD",
                    "code": "PEAK_HOUR_FEE",
                })
        
        return subtotal, lines
    
    @staticmethod
    def _find_fee_by_distance(
        service_rate: ServiceRate, total_distance: int
    ) -> Optional[ServiceRateFee]:
        """Find the appropriate fee tier based on distance."""
        if not service_rate.rate_fees:
            return None
        
        # Convert meters to kilometers
        distance_in_km = total_distance / 1000
        
        # Sort fees by distance
        sorted_fees = sorted(
            service_rate.rate_fees,
            key=lambda f: f.distance or 0
        )
        
        # Find first tier that covers the distance
        for fee in sorted_fees:
            if fee.distance and distance_in_km <= fee.distance:
                return fee
        
        # If distance exceeds all tiers, use the largest tier
        return sorted_fees[-1] if sorted_fees else None
    
    @staticmethod
    def _calculate_percentage(percent: int, amount: int) -> int:
        """Calculate percentage of amount."""
        return int((percent / 100) * amount)
    
    @staticmethod
    def _is_within_peak_hours(
        start_time: Optional[str], end_time: Optional[str]
    ) -> bool:
        """Check if current time is within peak hours."""
        if not start_time or not end_time:
            return False
        
        try:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            
            # Simple time comparison (HH:MM format)
            return start_time <= current_time <= end_time
        except Exception:
            return False
    
    @staticmethod
    def calculate_distance_meters(
        origin_lat: float, origin_lng: float,
        dest_lat: float, dest_lng: float
    ) -> int:
        """
        Calculate distance between two points using Haversine formula.
        Returns distance in meters.
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # Earth's radius in meters
        R = 6371000
        
        lat1_rad = radians(origin_lat)
        lat2_rad = radians(dest_lat)
        delta_lat = radians(dest_lat - origin_lat)
        delta_lng = radians(dest_lng - origin_lng)
        
        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lng / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        return int(distance)

