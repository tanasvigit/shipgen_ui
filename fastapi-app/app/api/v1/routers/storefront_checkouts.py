from typing import Any, Optional
import uuid
import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_checkout import StorefrontCheckout
from app.models.storefront_cart import StorefrontCart
from app.models.storefront_gateway import StorefrontGateway
from app.models.service_quote import ServiceQuote
from app.models.contact import Contact
from app.models.user import User
from app.schemas.storefront_checkout import (
    CheckoutInitialize,
    CheckoutStatusRequest,
    CheckoutCapture,
    CheckoutOut,
)

router = APIRouter(prefix="/storefront/v1/checkouts", tags=["storefront-checkouts"])


def generate_checkout_token() -> str:
    """Generate a unique checkout token."""
    random_str = secrets.token_hex(14)
    timestamp = str(uuid.uuid4())
    return f"checkout_{hashlib.md5((random_str + timestamp).encode()).hexdigest()}"


@router.get("/before", response_model=dict)
def before_checkout(
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    gateway: Optional[str] = None,
    customer: Optional[str] = None,
    cart: Optional[str] = None,
    serviceQuote: Optional[str] = None,
    service_quote: Optional[str] = None,
    cash: bool = Query(False),
    pickup: bool = Query(False),
    tip: Optional[Any] = None,
    deliveryTip: Optional[Any] = None,
    delivery_tip: Optional[Any] = None,
):
    """Initialize checkout session."""
    gateway_code = gateway or ("cash" if cash else None)
    customer_id = customer
    cart_id = cart
    service_quote_id = serviceQuote or service_quote
    is_cash_on_delivery = cash or gateway_code == "cash"
    is_pickup = pickup
    
    # Find cart
    cart_obj = (
        db.query(StorefrontCart)
        .filter((StorefrontCart.uuid == cart_id) | (StorefrontCart.public_id == cart_id))
        .first()
    )
    if not cart_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    
    # Find gateway
    gateway_obj = None
    if gateway_code and gateway_code != "cash":
        gateway_obj = (
            db.query(StorefrontGateway)
            .filter(StorefrontGateway.code == gateway_code)
            .first()
        )
        if not gateway_obj:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No gateway configured!")
    
    # Find customer
    customer_obj = None
    if customer_id:
        customer_obj = (
            db.query(Contact)
            .filter(Contact.company_uuid == current.company_uuid, (Contact.uuid == customer_id) | (Contact.public_id == customer_id))
            .first()
        )
    
    # Find service quote
    service_quote_obj = None
    if service_quote_id:
        service_quote_obj = (
            db.query(ServiceQuote)
            .filter((ServiceQuote.uuid == service_quote_id) | (ServiceQuote.public_id == service_quote_id))
            .first()
        )
    
    # Calculate amount (simplified)
    amount = cart_obj.subtotal or 0
    if service_quote_obj and not is_pickup:
        amount += service_quote_obj.amount or 0
    if tip:
        # Handle tip calculation (percentage or fixed)
        if isinstance(tip, str) and tip.endswith("%"):
            tip_amount = int((float(tip.rstrip("%")) / 100) * cart_obj.subtotal)
        else:
            tip_amount = int(tip) if tip else 0
        amount += tip_amount
    
    currency = cart_obj.currency or "USD"
    
    # Create checkout
    checkout = StorefrontCheckout()
    checkout.uuid = str(uuid.uuid4())
    checkout.company_uuid = current.company_uuid
    checkout.cart_uuid = cart_obj.uuid
    checkout.gateway_uuid = gateway_obj.uuid if gateway_obj else None
    checkout.service_quote_uuid = service_quote_obj.uuid if service_quote_obj else None
    checkout.owner_uuid = customer_obj.uuid if customer_obj else current.uuid
    checkout.owner_type = "fleet-ops:contact"
    checkout.amount = amount
    checkout.currency = currency
    checkout.is_cod = is_cash_on_delivery
    checkout.is_pickup = is_pickup
    checkout.options = {
        "is_pickup": is_pickup,
        "is_cod": is_cash_on_delivery,
        "tip": tip,
        "delivery_tip": deliveryTip or delivery_tip,
    }
    checkout.cart_state = {}  # Would store cart state
    checkout.token = generate_checkout_token()
    
    db.add(checkout)
    db.commit()
    db.refresh(checkout)
    
    # For cash orders, just return token
    if is_cash_on_delivery:
        return {"token": checkout.token}
    
    # For Stripe/QPay, would initialize payment here
    # Simplified - return token for now
    return {
        "token": checkout.token,
        "paymentIntent": None,  # Would be set for Stripe
        "clientSecret": None,  # Would be set for Stripe
        "ephemeralKey": None,  # Would be set for Stripe
        "customerId": None,  # Would be set for Stripe
    }


@router.get("/status", response_model=dict)
def get_checkout_status(
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    checkout: Optional[str] = None,
    token: Optional[str] = None,
):
    """Get checkout status including payment and order details."""
    if not checkout or not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required parameters: checkout and token")
    
    checkout_obj = (
        db.query(StorefrontCheckout)
        .filter(StorefrontCheckout.public_id == checkout, StorefrontCheckout.token == token)
        .first()
    )
    
    if not checkout_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checkout not found")
    
    # Get order if exists
    order = None
    if checkout_obj.order_uuid:
        from app.models.order import Order
        order = (
            db.query(Order)
            .filter(Order.uuid == checkout_obj.order_uuid)
            .first()
        )
    
    response = {
        "status": "completed" if checkout_obj.captured else "pending",
        "checkout": checkout_obj.public_id,
        "payment": None,
        "order": order.dict() if order else None,
    }
    
    # Check payment status for QPay/Stripe (simplified)
    if checkout_obj.gateway_uuid:
        gateway = (
            db.query(StorefrontGateway)
            .filter(StorefrontGateway.uuid == checkout_obj.gateway_uuid)
            .first()
        )
        if gateway and gateway.code == "qpay":
            # In production, would check QPay payment status
            pass
    
    return response


@router.post("/capture", response_model=dict)
def capture_order(
    payload: CheckoutCapture,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Capture and create order from checkout."""
    checkout = (
        db.query(StorefrontCheckout)
        .filter(StorefrontCheckout.token == payload.token)
        .first()
    )
    
    if not checkout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checkout not found")
    
    if checkout.captured and checkout.order_uuid:
        from app.models.order import Order
        order = (
            db.query(Order)
            .filter(Order.uuid == checkout.order_uuid)
            .first()
        )
        if order:
            return order.dict()
    
    # Create order from checkout (simplified - full implementation would create payload, entities, transaction, etc.)
    from app.models.order import Order
    order = Order()
    order.uuid = str(uuid.uuid4())
    order.company_uuid = current.company_uuid
    order.customer_uuid = checkout.owner_uuid
    order.customer_type = checkout.owner_type
    order.type = "storefront"
    order.status = "created"
    order.meta = {
        "checkout_id": checkout.public_id,
        "subtotal": checkout.amount,
        "currency": checkout.currency,
        "is_pickup": checkout.is_pickup,
    }
    order.notes = payload.notes
    
    db.add(order)
    
    # Update checkout
    checkout.order_uuid = order.uuid
    checkout.captured = True
    db.add(checkout)
    db.commit()
    db.refresh(order)
    
    return order.dict()


@router.post("/stripe-setup-intent", response_model=dict)
def create_stripe_setup_intent(
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    customer: Optional[str] = None,
):
    """Create Stripe setup intent for customer."""
    # Simplified - in production, would integrate with Stripe API
    gateway = (
        db.query(StorefrontGateway)
        .filter(StorefrontGateway.code == "stripe")
        .first()
    )
    
    if not gateway:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stripe not setup.")
    
    customer_obj = None
    if customer:
        customer_obj = (
            db.query(Contact)
            .filter(Contact.company_uuid == current.company_uuid, (Contact.uuid == customer) | (Contact.public_id == customer))
            .first()
        )
    
    # In production, would create Stripe SetupIntent
    return {
        "setupIntent": None,
        "clientSecret": None,
        "defaultPaymentMethod": None,
        "customerId": None,
    }


@router.put("/stripe-update-payment-intent", response_model=dict)
def update_stripe_payment_intent(
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    customer: Optional[str] = None,
    cart: Optional[str] = None,
    serviceQuote: Optional[str] = None,
    service_quote: Optional[str] = None,
    paymentIntent: Optional[str] = None,
    paymentIntentId: Optional[str] = None,
    payment_intent_id: Optional[str] = None,
    pickup: bool = Query(False),
    tip: Optional[Any] = None,
    deliveryTip: Optional[Any] = None,
    delivery_tip: Optional[Any] = None,
):
    """Update Stripe payment intent."""
    payment_intent_id = paymentIntent or paymentIntentId or payment_intent_id
    
    if not payment_intent_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment intent ID required")
    
    # In production, would update Stripe PaymentIntent
    return {
        "paymentIntent": payment_intent_id,
        "clientSecret": None,
        "ephemeralKey": None,
        "customerId": None,
        "token": None,
    }


@router.post("/capture-qpay", response_model=dict)
def capture_qpay_callback(
    request: Request,
    db: Session = Depends(get_db),
    checkout: Optional[str] = None,
    respond: bool = Query(False),
    test: Optional[str] = None,
):
    """Handle QPay callback."""
    if not checkout:
        return {
            "error": "CHECKOUT_ID_MISSING",
            "checkout": None,
            "payment": None,
        }
    
    checkout_obj = (
        db.query(StorefrontCheckout)
        .filter(StorefrontCheckout.public_id == checkout)
        .first()
    )
    
    if not checkout_obj:
        return {
            "error": "CHECKOUT_SESSION_NOT_FOUND",
            "checkout": None,
            "payment": None,
        }
    
    gateway = None
    if checkout_obj.gateway_uuid:
        gateway = (
            db.query(StorefrontGateway)
            .filter(StorefrontGateway.uuid == checkout_obj.gateway_uuid)
            .first()
        )
    
    if not gateway:
        return {
            "error": "GATEWAY_NOT_CONFIGURED",
            "checkout": checkout_obj.public_id,
            "payment": None,
        }
    
    # In production, would verify QPay payment
    # For now, return success
    return {
        "checkout": checkout_obj.public_id,
        "payment": None,
        "error": None,
    }

