"""
Storefront Cart model.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StorefrontCart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), unique=True, index=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    user_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    checkout_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # customer public_id
    unique_identifier: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Cart data
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    discount_code: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    items: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # Array of cart items
    events: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # Array of cart events
    
    # Expiry
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def calculate_subtotal(self) -> int:
        """Calculate subtotal from cart items."""
        if not self.items:
            return 0
        subtotal = 0
        for item in self.items:
            item_subtotal = item.get("subtotal", 0)
            if isinstance(item_subtotal, str):
                # Extract numbers only
                item_subtotal = int("".join(filter(str.isdigit, item_subtotal)))
            subtotal += item_subtotal
        return subtotal
    
    def get_total_items(self) -> int:
        """Get total quantity of items in cart."""
        if not self.items:
            return 0
        total = 0
        for item in self.items:
            quantity = item.get("quantity", 0)
            if isinstance(quantity, str):
                quantity = int(quantity)
            total += quantity
        return total
    
    def get_total_unique_items(self) -> int:
        """Get count of unique items in cart."""
        return len(self.items) if self.items else 0

