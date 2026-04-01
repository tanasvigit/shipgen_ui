from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash
from app.models.twofa import TwoFaSetting
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.api.v1.routers.auth import _get_current_user

router = APIRouter(prefix="/int/v1/users", tags=["users"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.get("/", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(User).filter(User.deleted_at.is_(None))
    users = query.offset(offset).limit(limit).all()
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
    _current: User = Depends(_get_current_user),
):
    user = db.query(User).filter(User.uuid == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    user = User()
    user.name = payload.name
    user.email = payload.email
    user.phone = payload.phone
    user.company_uuid = payload.company_uuid
    user.timezone = payload.timezone
    user.country = payload.country
    if payload.password:
        user.password = get_password_hash(payload.password)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.put("/{user_id}", response_model=UserOut)
@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    user = db.query(User).filter(User.uuid == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    user = db.query(User).filter(User.uuid == user_id).first()
    if not user:
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


