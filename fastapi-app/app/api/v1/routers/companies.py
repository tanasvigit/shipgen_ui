from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.company import Company
from app.models.company_user import CompanyUser
from app.models.twofa import TwoFaSetting
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyOut, CompanyUpdate
from app.schemas.user import UserOut
from app.api.v1.routers.auth import _get_current_user

router = APIRouter(prefix="/int/v1/companies", tags=["companies"])


# --- Schemas for additional endpoints ---
class TwoFaSettingsBody(BaseModel):
    twoFaSettings: Optional[dict] = None


class TransferOwnershipRequest(BaseModel):
    company: str
    newOwner: str
    leave: bool = False


class LeaveOrganizationRequest(BaseModel):
    company: str
    user: Optional[str] = None


# --- Static routes MUST be defined before /{company_id} ---

@router.get("/two-fa")
def get_company_twofa_settings(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Get current company's two-factor authentication settings."""
    if not current.company_uuid:
        raise HTTPException(status_code=400, detail="Current user is not associated with a company.")
    settings = (
        db.query(TwoFaSetting)
        .filter(TwoFaSetting.subject_type == "company", TwoFaSetting.subject_uuid == current.company_uuid)
        .first()
    )
    if not settings:
        return {"enabled": False, "method": "email", "enforced": False}
    return {"enabled": settings.enabled, "method": settings.method, "enforced": settings.enforced}


@router.post("/two-fa")
def save_company_twofa_settings(
    payload: TwoFaSettingsBody,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Save two-factor authentication settings for current company. Matches PHP CompanyController::saveTwoFactorSettings."""
    if not current.company_uuid:
        raise HTTPException(status_code=400, detail="Current user is not associated with a company.")
    two_fa = (payload.twoFaSettings or {})
    enabled = two_fa.get("enabled", False)
    method = two_fa.get("method", "email")
    enforced = two_fa.get("enforced", False) if enabled else False
    settings = (
        db.query(TwoFaSetting)
        .filter(TwoFaSetting.subject_type == "company", TwoFaSetting.subject_uuid == current.company_uuid)
        .first()
    )
    if not settings:
        settings = TwoFaSetting(subject_type="company", subject_uuid=current.company_uuid)
    settings.enabled = enabled
    settings.method = method
    settings.enforced = enforced
    db.add(settings)
    db.commit()
    return {"message": "Two-Factor Authentication saved successfully"}


@router.get("/find/{id}", response_model=CompanyOut)
def find_company(
    id: str,
    db: Session = Depends(get_db),
):
    """Find company by public_id (company_xxx) or UUID. Matches PHP CompanyController::findCompany."""
    lookup_id = id.strip()
    company = None
    if lookup_id.startswith("company_"):
        company = db.query(Company).filter(Company.public_id == lookup_id, Company.deleted_at.is_(None)).first()
    else:
        company = db.query(Company).filter(Company.uuid == lookup_id, Company.deleted_at.is_(None)).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")
    return company


@router.post("/transfer-ownership")
def transfer_ownership(
    payload: TransferOwnershipRequest,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Transfer company ownership to another member. Matches PHP CompanyController::transferOwnership."""
    company = db.query(Company).filter(Company.uuid == payload.company).first()
    if not company:
        raise HTTPException(status_code=400, detail="No organization found to transfer ownership for.")
    cu = (
        db.query(CompanyUser)
        .filter(
            CompanyUser.company_uuid == payload.company,
            CompanyUser.user_uuid == payload.newOwner,
            CompanyUser.deleted_at.is_(None),
        )
        .first()
    )
    if not cu:
        raise HTTPException(status_code=400, detail="The new owner provided could not be found for transfer of ownership.")
    new_owner = db.query(User).filter(User.uuid == payload.newOwner).first()
    if not new_owner:
        raise HTTPException(status_code=400, detail="The new owner provided could not be found for transfer of ownership.")
    company.owner_uuid = new_owner.uuid
    db.add(company)
    admin_role = db.execute(text("SELECT id FROM roles WHERE name = 'Administrator' AND guard_name = 'sanctum'")).fetchone()
    if admin_role:
        db.execute(
            text("DELETE FROM model_has_roles WHERE model_uuid = :mu AND model_type = 'Fleetbase\\Models\\CompanyUser'"),
            {"mu": cu.uuid},
        )
        db.execute(
            text("INSERT INTO model_has_roles (role_id, model_type, model_uuid) VALUES (:rid, 'Fleetbase\\Models\\CompanyUser', :mu)"),
            {"rid": admin_role[0], "mu": cu.uuid},
        )
    if payload.leave:
        current_cu = (
            db.query(CompanyUser)
            .filter(
                CompanyUser.company_uuid == payload.company,
                CompanyUser.user_uuid == current.uuid,
                CompanyUser.deleted_at.is_(None),
            )
            .first()
        )
        if current_cu:
            from datetime import datetime, timezone
            current_cu.deleted_at = current_cu.updated_at or datetime.now(timezone.utc)
            db.add(current_cu)
        next_cu = (
            db.query(CompanyUser)
            .filter(
                CompanyUser.user_uuid == current.uuid,
                CompanyUser.company_uuid != company.uuid,
                CompanyUser.deleted_at.is_(None),
            )
            .first()
        )
        next_company = db.query(Company).filter(Company.uuid == next_cu.company_uuid).first() if next_cu else None
        if next_company:
            current.company_uuid = next_company.uuid
            db.add(current)
    db.commit()
    return {"status": "ok", "newOwner": new_owner.uuid, "currentUserLeft": payload.leave}


@router.post("/leave")
def leave_organization(
    payload: LeaveOrganizationRequest,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Remove current user from organization. Matches PHP CompanyController::leaveOrganization."""
    user_to_leave = current
    if payload.user:
        user_to_leave = db.query(User).filter(User.uuid == payload.user).first()
    if not user_to_leave:
        raise HTTPException(status_code=400, detail="Unable to leave organization.")
    company = db.query(Company).filter(Company.uuid == payload.company).first()
    if not company:
        raise HTTPException(status_code=400, detail="No organization found for user to leave.")
    current_cu = (
        db.query(CompanyUser)
        .filter(
            CompanyUser.company_uuid == payload.company,
            CompanyUser.user_uuid == user_to_leave.uuid,
            CompanyUser.deleted_at.is_(None),
        )
        .first()
    )
    if not current_cu:
        raise HTTPException(status_code=400, detail="User selected to leave organization is not a member of this organization.")
    from datetime import datetime, timezone
    current_cu.deleted_at = datetime.now(timezone.utc)
    db.add(current_cu)
    next_cu = (
        db.query(CompanyUser)
        .filter(
            CompanyUser.user_uuid == user_to_leave.uuid,
            CompanyUser.company_uuid != company.uuid,
            CompanyUser.deleted_at.is_(None),
        )
        .first()
    )
    next_company = db.query(Company).filter(Company.uuid == next_cu.company_uuid).first() if next_cu else None
    if next_company:
        user_to_leave.company_uuid = next_company.uuid
        db.add(user_to_leave)
    db.commit()
    return {"status": "ok"}


# --- CRUD routes ---

@router.get("/", response_model=List[CompanyOut])
def list_companies(
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(Company).filter(Company.deleted_at.is_(None))
    companies = query.offset(offset).limit(limit).all()
    return companies


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    company = db.query(Company).filter(Company.uuid == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")
    return company


@router.post("/", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_company(
    payload: CompanyCreate,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    company = Company()
    company.name = payload.name
    company.description = payload.description
    company.phone = payload.phone
    company.website_url = payload.website_url
    company.currency = payload.currency
    company.country = payload.country
    company.timezone = payload.timezone

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


@router.put("/{company_id}", response_model=CompanyOut)
@router.patch("/{company_id}", response_model=CompanyOut)
def update_company(
    company_id: str,
    payload: CompanyUpdate,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    company = db.query(Company).filter(Company.uuid == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(company, field, value)

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    company = db.query(Company).filter(Company.uuid == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    company.deleted_at = company.deleted_at or company.updated_at
    db.add(company)
    db.commit()


@router.get("/{company_id}/users", response_model=List[UserOut])
def company_users(
    company_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    company = db.query(Company).filter(Company.uuid == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    user_uuids = (
        db.query(CompanyUser.user_uuid)
        .filter(CompanyUser.company_uuid == company.uuid)
        .filter(CompanyUser.deleted_at.is_(None))
        .all()
    )
    ids = [u[0] for u in user_uuids]
    if not ids:
        return []

    users = db.query(User).where(User.uuid.in_(ids)).all()
    return users

