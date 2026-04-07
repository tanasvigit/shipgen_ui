from datetime import datetime, timedelta, timezone
import hashlib
import json
from typing import Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.cache import get_redis
from app.core.database import get_db
from app.core.roles import effective_user_role
from app.core.security import create_access_token, decode_access_token, verify_password
from app.models.company import Company
from app.models.company_user import CompanyUser
from app.models.twofa import TwoFaSetting, TwoFaSession
from app.models.user import User
from app.schemas.auth import (
    BootstrapResponse,
    InstallerStatus,
    LoginRequest,
    LoginResponse,
    LoginUser,
    OrganizationSummary,
    OrganizationsResponse,
    SessionData,
)

router = APIRouter(prefix="/int/v1/auth")
bearer_scheme = HTTPBearer(auto_error=False)


def _build_session(user: User, token: str) -> SessionData:
    return SessionData(
        id=user.uuid,
        token=token,
        user=user.uuid,
        verified=user.email_verified_at is not None,
        type=user.type,
        last_modified=user.updated_at,
    )


def _get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthenticated.")

    try:
        payload = decode_access_token(creds.credentials)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

    user = db.query(User).filter(User.uuid == sub).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

    return user


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    # Accept either identity or email (console may send either)
    identity = (payload.identity or payload.email or "").strip()
    password = payload.password
    auth_token = payload.authToken

    if not identity and not auth_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identity or email is required.",
        )

    # If attempting to authenticate with auth token, validate it
    if auth_token:
        try:
            decoded = decode_access_token(auth_token)
            user = db.query(User).filter(User.uuid == decoded.get("sub")).first()
            if user and (not user.deleted_at):
                login_user = LoginUser(
                    id=user.uuid or str(user.id),
                    email=user.email,
                    name=user.name,
                    role=effective_user_role(user),
                )
                return LoginResponse(token=auth_token, user=login_user, type=user.type)
        except Exception:
            pass

    user = (
        db.query(User)
        .filter(
            (User.email == identity) | (User.phone == identity),
            User.deleted_at.is_(None),
        )
        .first()
    )

    # 400 = no such user (identity not found); 401 = wrong password
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user found by the provided identity.",
        )

    # Check if 2FA enabled (system-wide simplified check)
    twofa_settings = db.query(TwoFaSetting).filter(TwoFaSetting.subject_type == "system").first()
    if twofa_settings and twofa_settings.enabled:
        # Generate 2FA session
        import secrets
        import string
        session_token = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(40))
        
        twofa_session = TwoFaSession(
            identity=identity,
            session_token=session_token,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(twofa_session)
        db.commit()
        
        return LoginResponse(twoFaSession=session_token, isEnabled=True)

    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required.",
        )
    if not user.password or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed using password provided.",
        )

    user.last_login = datetime.now(timezone.utc).isoformat()
    db.add(user)
    db.commit()

    token = create_access_token(subject=user.uuid, token_type=user.type)
    login_user = LoginUser(
        id=user.uuid or str(user.id),
        email=user.email,
        name=user.name,
        role=effective_user_role(user),
    )
    return LoginResponse(token=token, user=login_user, type=user.type)


@router.get("/session", response_model=SessionData)
def session(
    response: Response,
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session has expired.")

    token = creds.credentials
    redis = get_redis()
    cache_key = f"session_validation_{token}"
    
    session_data_dict = None
    cache_hit = False

    # Try to get from cache
    if redis:
        try:
            cached = redis.get(cache_key)
            if cached:
                session_data_dict = json.loads(cached)
                cache_hit = True
        except Exception:
            pass

    if not session_data_dict:
        # Get user and build session
        user = _get_current_user(creds, db)
        session_data = _build_session(user, token)
        session_data_dict = session_data.dict()

        # Try to cache
        if redis:
            try:
                redis.setex(cache_key, 300, json.dumps(session_data_dict, default=str))
            except Exception:
                pass

    # Generate ETag
    etag = hashlib.sha1(json.dumps(session_data_dict, sort_keys=True, default=str).encode()).hexdigest()
    
    # Set headers
    response.headers["ETag"] = f'"{etag}"'
    if session_data_dict.get("last_modified"):
        response.headers["Last-Modified"] = str(session_data_dict["last_modified"])
    response.headers["Cache-Control"] = "private, no-cache, must-revalidate"
    response.headers["X-Cache-Hit"] = "true" if cache_hit else "false"

    return session_data_dict


@router.post("/logout")
def logout(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    """Logout endpoint - invalidates session token. Works even without auth token for CORS preflight."""
    if creds is None:
        # Allow logout even without token (for CORS preflight and graceful handling)
        return {"message": "Logged out"}

    token = creds.credentials
    try:
        redis = get_redis()
        if redis:
            redis.delete(f"session_validation_{token}")
    except Exception:
        # If Redis fails, still return success (token will expire naturally)
        pass

    return {"message": "Logged out"}


def _company_to_org_summary(org: Company) -> OrganizationSummary:
    return OrganizationSummary(
        id=org.uuid,
        uuid=org.uuid,
        public_id=org.public_id,
        name=org.name,
        description=org.description,
        phone=org.phone,
        timezone=org.timezone,
        country=org.country,
        currency=org.currency,
        status=org.status,
    )


@router.get("/organizations", response_model=OrganizationsResponse)
def get_organizations(
    user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    """Return organizations (companies) for the current user. Used by console after login."""
    organizations_rows = (
        db.query(Company)
        .join(CompanyUser, Company.uuid == CompanyUser.company_uuid)
        .filter(CompanyUser.user_uuid == user.uuid)
        .filter(CompanyUser.deleted_at.is_(None))
        .filter(Company.owner_uuid.isnot(None))
        .all()
    )
    organizations = [_company_to_org_summary(org) for org in organizations_rows]
    # Fallback: if user has company_uuid but no orgs from join (e.g. missing CompanyUser), return that company so console does not log out
    if not organizations and user.company_uuid:
        company = db.query(Company).filter(Company.uuid == user.company_uuid).first()
        if company:
            organizations = [_company_to_org_summary(company)]
    return OrganizationsResponse(organizations=organizations, company=organizations)


@router.get("/bootstrap", response_model=BootstrapResponse)
def bootstrap(
    response: Response,
    user: User = Depends(_get_current_user),
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthenticated.")

    token = creds.credentials
    redis = get_redis()
    cache_key = f"auth_bootstrap_{user.uuid}_{token}"

    cached = None
    if redis:
        try:
            cached = redis.get(cache_key)
        except Exception:
            pass

    if cached:
        payload_dict = json.loads(cached)
    else:
        session_data = _build_session(user, token)

        organizations_rows = (
            db.query(Company)
            .join(CompanyUser, Company.uuid == CompanyUser.company_uuid)
            .filter(CompanyUser.user_uuid == user.uuid)
            .filter(CompanyUser.deleted_at.is_(None))
            .filter(Company.owner_uuid.isnot(None))
            .all()
        )

        organizations = [_company_to_org_summary(org) for org in organizations_rows]
        if not organizations and user.company_uuid:
            company = db.query(Company).filter(Company.uuid == user.company_uuid).first()
            if company:
                organizations = [_company_to_org_summary(company)]

        # In production, this would check installer status properly
        installer = InstallerStatus(
            shouldInstall=False,
            shouldOnboard=False,
            defaultTheme="dark",
        )

        payload = BootstrapResponse(
            session=session_data,
            organizations=organizations,
            installer=installer,
        )
        payload_dict = payload.dict()

        if redis:
            try:
                redis.setex(cache_key, 300, json.dumps(payload_dict, default=str))
            except Exception:
                pass

    response.headers["Cache-Control"] = "private, max-age=300"
    return payload_dict



