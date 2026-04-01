import random
import string
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.twofa import TwoFaSetting, TwoFaSession
from app.models.user import User
from app.schemas.twofa import (
    TwoFaCheckRequest,
    TwoFaCheckResponse,
    TwoFaEnforceResponse,
    TwoFaInvalidateRequest,
    TwoFaInvalidateResponse,
    TwoFaResendRequest,
    TwoFaResendResponse,
    TwoFaSettings,
    TwoFaValidateRequest,
    TwoFaValidateResponse,
    TwoFaVerifyRequest,
    TwoFaVerifyResponse,
)

router = APIRouter(prefix="/int/v1/two-fa", tags=["two-fa"])


def _get_system_settings(db: Session) -> TwoFaSetting:
    settings = (
        db.query(TwoFaSetting)
        .filter(TwoFaSetting.subject_type == "system", TwoFaSetting.subject_uuid.is_(None))
        .first()
    )
    if not settings:
        settings = TwoFaSetting(subject_type="system", subject_uuid=None, enabled=False, method="email", enforced=False)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.post("/config", response_model=TwoFaSettings)
def save_system_config(
    payload: TwoFaSettings,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    settings = _get_system_settings(db)
    settings.enabled = payload.enabled
    # If disabled, enforced must be false
    settings.enforced = payload.enforced if payload.enabled else False
    settings.method = payload.method
    settings.updated_at = datetime.now(timezone.utc)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return TwoFaSettings(enabled=settings.enabled, method=settings.method, enforced=settings.enforced)


@router.get("/config", response_model=TwoFaSettings)
def get_system_config(
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    settings = _get_system_settings(db)
    return TwoFaSettings(enabled=settings.enabled, method=settings.method, enforced=settings.enforced)


@router.get("/enforce", response_model=TwoFaEnforceResponse)
def should_enforce(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    settings = _get_system_settings(db)
    # Simple rule: enforce only if globally enforced and user has a company
    should_enforce = settings.enabled and settings.enforced and current.company_uuid is not None
    return TwoFaEnforceResponse(shouldEnforce=should_enforce)


def _generate_token(length: int = 40) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def _generate_code() -> str:
    return f"{random.randint(100000, 999999)}"


@router.get("/check", response_model=TwoFaCheckResponse)
def check_two_factor_get(
    identity: str = Query(..., description="User identity (email or phone)"),
    db: Session = Depends(get_db),
):
    """Check if 2FA is enabled for a user identity (GET with query parameter)."""
    settings = _get_system_settings(db)
    if not settings.enabled:
        return TwoFaCheckResponse(twoFaSession=None, isTwoFaEnabled=False)

    # Create a session token and store an initial record with no code yet
    token = _generate_token()
    now = datetime.now(timezone.utc)
    session = TwoFaSession(
        identity=identity,
        session_token=token,
        code=None,
        expires_at=now + timedelta(minutes=10),
        created_at=now,
        updated_at=now,
    )
    db.add(session)
    db.commit()

    return TwoFaCheckResponse(twoFaSession=token, isTwoFaEnabled=True)


@router.post("/check", response_model=TwoFaCheckResponse)
def check_two_factor_post(
    payload: TwoFaCheckRequest,
    db: Session = Depends(get_db),
):
    """Check if 2FA is enabled for a user identity (POST with request body)."""
    settings = _get_system_settings(db)
    if not settings.enabled:
        return TwoFaCheckResponse(twoFaSession=None, isTwoFaEnabled=False)

    # Create a session token and store an initial record with no code yet
    token = _generate_token()
    now = datetime.now(timezone.utc)
    session = TwoFaSession(
        identity=payload.identity,
        session_token=token,
        code=None,
        expires_at=now + timedelta(minutes=10),
        created_at=now,
        updated_at=now,
    )
    db.add(session)
    db.commit()

    return TwoFaCheckResponse(twoFaSession=token, isTwoFaEnabled=True)
    
    settings = _get_system_settings(db)
    if not settings.enabled:
        return TwoFaCheckResponse(twoFaSession=None, isTwoFaEnabled=False)

    # Create a session token and store an initial record with no code yet
    token = _generate_token()
    now = datetime.now(timezone.utc)
    session = TwoFaSession(
        identity=user_identity,
        session_token=token,
        code=None,
        expires_at=now + timedelta(minutes=10),
        created_at=now,
        updated_at=now,
    )
    db.add(session)
    db.commit()

    return TwoFaCheckResponse(twoFaSession=token, isTwoFaEnabled=True)


@router.post("/validate", response_model=TwoFaValidateResponse)
def validate_session(
    payload: TwoFaValidateRequest,
    db: Session = Depends(get_db),
):
    session = (
        db.query(TwoFaSession)
        .filter(TwoFaSession.session_token == payload.token, TwoFaSession.identity == payload.identity)
        .first()
    )
    if not session or (session.expires_at and session.expires_at < datetime.now(timezone.utc)):
        return TwoFaValidateResponse(clientToken=None, expired=True)

    # If clientToken already provided, just confirm it is valid
    if payload.clientToken and session.client_token == payload.clientToken:
        return TwoFaValidateResponse(clientToken=payload.clientToken, expired=False)

    # Generate a code and clientToken, as in Laravel flow
    session.code = _generate_code()
    session.client_token = _generate_token(32)
    session.expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    session.updated_at = datetime.now(timezone.utc)
    db.add(session)
    db.commit()

    # NOTE: In production, you would send the code via email/SMS here.

    return TwoFaValidateResponse(clientToken=session.client_token, expired=False)


@router.post("/verify", response_model=TwoFaVerifyResponse)
def verify_code(
    payload: TwoFaVerifyRequest,
    db: Session = Depends(get_db),
):
    session = (
        db.query(TwoFaSession)
        .filter(
            TwoFaSession.session_token == payload.token,
            TwoFaSession.client_token == payload.clientToken,
        )
        .first()
    )
    if not session or not session.code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 2FA session.")

    if session.expires_at and session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA code has expired.")

    if payload.code != session.code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 2FA code.")

    session.validated_at = datetime.now(timezone.utc)
    db.add(session)
    db.commit()

    # For FastAPI, we can simply echo back the clientToken as authToken equivalent
    return TwoFaVerifyResponse(authToken=session.client_token or "")


@router.post("/resend", response_model=TwoFaResendResponse)
def resend_code(
    payload: TwoFaResendRequest,
    db: Session = Depends(get_db),
):
    session = (
        db.query(TwoFaSession)
        .filter(TwoFaSession.session_token == payload.token, TwoFaSession.identity == payload.identity)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 2FA session.")

    session.code = _generate_code()
    session.client_token = _generate_token(32)
    session.expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    session.updated_at = datetime.now(timezone.utc)
    db.add(session)
    db.commit()

    # In production, send new code via email/SMS.

    return TwoFaResendResponse(clientToken=session.client_token)


@router.post("/invalidate", response_model=TwoFaInvalidateResponse)
def invalidate_session(
    payload: TwoFaInvalidateRequest,
    db: Session = Depends(get_db),
):
    session = (
        db.query(TwoFaSession)
        .filter(TwoFaSession.session_token == payload.token, TwoFaSession.identity == payload.identity)
        .first()
    )
    if not session:
        return TwoFaInvalidateResponse(ok=False)

    db.delete(session)
    db.commit()
    return TwoFaInvalidateResponse(ok=True)



