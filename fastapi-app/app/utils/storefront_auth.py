"""
Storefront authentication utilities.
"""
from typing import Optional
from fastapi import HTTPException, status, Header
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.core.security import decode_access_token


def get_storefront_customer(
    db: Session,
    authorization: Optional[str] = Header(None)
) -> Optional[Contact]:
    """
    Extract and validate storefront customer from Authorization header.
    Returns Contact object if valid, None otherwise.
    """
    if not authorization:
        return None
    
    try:
        # Extract token from "Bearer <token>" format
        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        else:
            token = authorization
        
        # Decode token
        payload = decode_access_token(token)
        if not payload:
            return None
        
        # Check if token is for a customer (not internal user)
        token_type = payload.get("type", "user")
        if token_type != "customer":
            return None
        
        # Get customer UUID from token
        customer_uuid = payload.get("sub")
        if not customer_uuid:
            return None
        
        # Fetch customer from database
        customer = db.query(Contact).filter(
            Contact.uuid == customer_uuid,
            Contact.type == "customer",
            Contact.deleted_at.is_(None)
        ).first()
        
        return customer
    except Exception:
        return None


def require_storefront_customer(
    db: Session,
    authorization: Optional[str] = Header(None)
) -> Contact:
    """
    Require valid storefront customer authentication.
    Raises HTTPException if not authenticated.
    """
    customer = get_storefront_customer(db, authorization)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer authentication required"
        )
    return customer

