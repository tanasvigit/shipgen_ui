from typing import Optional, Any
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.company_user import CompanyUser
from app.models.role import Role
from app.core.security import get_password_hash
from app.utils.verification import (
    generate_verification_code,
    store_verification_code,
    verify_code,
    send_verification_email,
    send_verification_sms
)

router = APIRouter(prefix="/int/v1/onboard", tags=["onboard"])


class CreateAccountRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    company_name: str


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str


class SendVerificationRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


@router.get("/should-onboard", response_model=dict)
def should_onboard(
    db: Session = Depends(get_db),
):
    """Check if user should be onboarded."""
    user_count = db.query(User).filter(User.deleted_at.is_(None)).count()
    company_count = db.query(Company).filter(Company.deleted_at.is_(None)).count()
    
    should_onboard = user_count == 0 or company_count == 0
    
    return {
        "should_onboard": should_onboard,
        "reason": "No users found in system" if user_count == 0 else "System already initialized",
        "user_count": user_count,
        "company_count": company_count
    }


@router.post("/create-account", response_model=dict)
def create_account(
    payload: CreateAccountRequest,
    db: Session = Depends(get_db),
):
    """Create a new account with user and company."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        User.email == payload.email,
        User.deleted_at.is_(None)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create company
    company_uuid = str(uuid.uuid4())
    company = Company(
        uuid=company_uuid,
        public_id=f"comp_{uuid.uuid4().hex[:12]}",
        name=payload.company_name,
        status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(company)
    db.flush()
    
    # Create user
    user_uuid = str(uuid.uuid4())
    user = User(
        uuid=user_uuid,
        public_id=f"user_{uuid.uuid4().hex[:12]}",
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        password=get_password_hash(payload.password),
        company_uuid=company_uuid,
        type="admin",
        status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.flush()
    
    # Set company owner
    company.owner_uuid = user_uuid
    db.add(company)
    
    # Create company-user relationship
    company_user = CompanyUser(
        uuid=str(uuid.uuid4()),
        company_uuid=company_uuid,
        user_uuid=user_uuid,
        status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(company_user)
    
    # Create or assign admin role
    admin_role = db.query(Role).filter(
        Role.name == "admin",
        Role.guard_name == "web"
    ).first()
    
    if not admin_role:
        admin_role = Role(
            id=str(uuid.uuid4()),
            name="admin",
            guard_name="web",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(admin_role)
    
    db.commit()
    
    return {
        "status": "ok",
        "message": "Account created successfully",
        "user_uuid": user_uuid,
        "company_uuid": company_uuid,
        "email": payload.email
    }


@router.post("/verify-email", response_model=dict)
def verify_email(
    payload: VerifyEmailRequest,
    db: Session = Depends(get_db),
):
    """Verify email with code."""
    # Verify code
    if not verify_code(payload.email, payload.code, "email"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Update user email_verified_at
    user = db.query(User).filter(
        User.email == payload.email,
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.email_verified_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    
    return {
        "status": "ok",
        "message": "Email verified successfully",
        "email": payload.email
    }


@router.post("/send-verification-sms", response_model=dict)
def send_verification_sms_endpoint(
    payload: SendVerificationRequest,
    db: Session = Depends(get_db),
):
    """Send SMS verification code."""
    if not payload.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is required"
        )
    
    # Generate and store code
    code = generate_verification_code()
    store_verification_code(payload.phone, code, "sms")
    
    # Send SMS
    send_verification_sms(payload.phone, code)
    
    return {
        "status": "ok",
        "message": "Verification code sent",
        "phone": payload.phone
    }


@router.post("/send-verification-email", response_model=dict)
def send_verification_email_endpoint(
    payload: SendVerificationRequest,
    db: Session = Depends(get_db),
):
    """Send email verification code."""
    if not payload.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required"
        )
    
    # Generate and store code
    code = generate_verification_code()
    store_verification_code(payload.email, code, "email")
    
    # Send email
    send_verification_email(payload.email, code)
    
    return {
        "status": "ok",
        "message": "Verification code sent",
        "email": payload.email
    }

