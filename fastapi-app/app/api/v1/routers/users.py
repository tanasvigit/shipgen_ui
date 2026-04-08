from typing import List
import uuid as uuidlib

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.core.roles import ADMIN, ALL_ROLES, DISPATCHER, require_roles
from app.core.security import get_password_hash, verify_password
from app.models.driver import Driver
from app.models.twofa import TwoFaSetting
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/int/v1/users", tags=["users"])
bearer_scheme = HTTPBearer(auto_error=False)


def _normalize_role(raw: str | None) -> str:
    r = (raw or DISPATCHER).strip().upper()
    return r if r in ALL_ROLES else DISPATCHER


def _normalize_user_uuid_or_422(raw: str) -> str:
    text = (raw or "").strip()
    try:
        return str(uuidlib.UUID(text))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="user_id must be a valid UUID.",
        ) from exc


def _ensure_user_identifiers(user: User) -> bool:
    changed = False
    if not user.uuid:
        user.uuid = str(uuidlib.uuid4())
        changed = True
    if not user.public_id:
        user.public_id = f"user_{uuidlib.uuid4().hex[:12]}"
        changed = True
    return changed


def _provision_driver_for_user_if_needed(db: Session, user: User) -> None:
    if not user.uuid or not user.company_uuid:
        return
    if _normalize_role(user.role) != "DRIVER":
        return
    existing = (
        db.query(Driver)
        .filter(
            Driver.company_uuid == user.company_uuid,
            Driver.user_uuid == user.uuid,
            Driver.deleted_at.is_(None),
        )
        .first()
    )
    if existing:
        return
    driver = Driver()
    driver.uuid = str(uuidlib.uuid4())
    driver.public_id = f"driver_{uuidlib.uuid4().hex[:12]}"
    driver.company_uuid = user.company_uuid
    driver.user_uuid = user.uuid
    driver.drivers_license_number = None
    driver.status = "active"
    driver.online = 0
    db.add(driver)


def _deactivate_driver_for_user_if_needed(db: Session, user: User) -> None:
    if not user.uuid or not user.company_uuid:
        return
    driver = (
        db.query(Driver)
        .filter(
            Driver.company_uuid == user.company_uuid,
            Driver.user_uuid == user.uuid,
            Driver.deleted_at.is_(None),
        )
        .first()
    )
    if not driver:
        return
    driver.status = "inactive"
    driver.online = 0
    db.add(driver)


@router.get("/", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN)),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(User).filter(User.deleted_at.is_(None))
    if current.company_uuid:
        query = query.filter(User.company_uuid == current.company_uuid)
    users = query.offset(offset).limit(limit).all()
    touched = False
    for u in users:
        if _ensure_user_identifiers(u):
            db.add(u)
            touched = True
    if touched:
        db.commit()
        for u in users:
            db.refresh(u)
    return users


@router.get("/me", response_model=UserOut)
def current_user(
    current: User = Depends(_get_current_user),
):
    """Get current authenticated user. Must be defined before /{user_id} route."""
    return current


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN)),
):
    user_uuid = _normalize_user_uuid_or_422(user_id)
    user = db.query(User).filter(User.uuid == user_uuid).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if current.company_uuid and user.company_uuid and user.company_uuid != current.company_uuid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN)),
):
    if not payload.role:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="role is required.")
    user = User()
    user.uuid = str(uuidlib.uuid4())
    user.public_id = f"user_{uuidlib.uuid4().hex[:12]}"
    user.name = payload.name
    user.email = payload.email
    user.phone = payload.phone
    user.company_uuid = payload.company_uuid or current.company_uuid
    user.timezone = payload.timezone
    user.country = payload.country
    user.role = _normalize_role(payload.role)
    if payload.password:
        user.password = get_password_hash(payload.password)

    db.add(user)
    _provision_driver_for_user_if_needed(db, user)
    db.commit()
    db.refresh(user)

    return user


@router.put("/{user_id}", response_model=UserOut)
@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN)),
):
    user_uuid = _normalize_user_uuid_or_422(user_id)
    user = db.query(User).filter(User.uuid == user_uuid).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if current.company_uuid and user.company_uuid and user.company_uuid != current.company_uuid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    old_role = _normalize_role(user.role)
    data = payload.model_dump(exclude_unset=True)
    if "role" in data:
        user.role = _normalize_role(data.pop("role"))
    for field, value in data.items():
        setattr(user, field, value)

    new_role = _normalize_role(user.role)
    if old_role != "DRIVER" and new_role == "DRIVER":
        _provision_driver_for_user_if_needed(db, user)
    if old_role == "DRIVER" and new_role != "DRIVER":
        _deactivate_driver_for_user_if_needed(db, user)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN)),
):
    user_uuid = _normalize_user_uuid_or_422(user_id)
    user = db.query(User).filter(User.uuid == user_uuid).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if current.company_uuid and user.company_uuid and user.company_uuid != current.company_uuid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.deleted_at = user.deleted_at or user.updated_at
    db.add(user)
    db.commit()


@router.post("/set-password")
def set_current_user_password(
    password: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    if not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is required.")

    current.password = get_password_hash(password)
    db.add(current)
    db.commit()

    return {"status": "ok"}


@router.post("/validate-password")
def validate_password(
    password: str,
    current: User = Depends(_get_current_user),
):
    if not current.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No password set.")

    if not verify_password(password, current.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password.")

    return {"status": "valid"}


@router.get("/two-fa")
def get_twofa_settings(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    settings = (
        db.query(TwoFaSetting)
        .filter(TwoFaSetting.subject_type == "user", TwoFaSetting.subject_uuid == current.uuid)
        .first()
    )
    if not settings:
        return {"enabled": False, "method": "email", "enforced": False}
    return {"enabled": settings.enabled, "method": settings.method, "enforced": settings.enforced}


@router.post("/two-fa")
def save_twofa_settings(
    enabled: bool,
    method: str = "email",
    enforced: bool = False,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    settings = (
        db.query(TwoFaSetting)
        .filter(TwoFaSetting.subject_type == "user", TwoFaSetting.subject_uuid == current.uuid)
        .first()
    )
    if not settings:
        settings = TwoFaSetting(subject_type="user", subject_uuid=current.uuid)

    settings.enabled = enabled
    settings.method = method
    settings.enforced = enforced if enabled else False
    db.add(settings)
    db.commit()
    return {"enabled": settings.enabled, "method": settings.method, "enforced": settings.enforced}


@router.get("/locale")
def get_user_locale(
    current: User = Depends(_get_current_user),
):
    """
    Minimal locale endpoint for console app.
    Returns a default locale and the user's timezone when available.
    """
    return {
        "locale": "en",
        "timezone": getattr(current, "timezone", None) or "UTC",
        "country": getattr(current, "country", None),
    }


