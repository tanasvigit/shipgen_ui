import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.api_credential import ApiCredential
from app.models.user import User

router = APIRouter(prefix="/int/v1/api-credentials", tags=["api-credentials"])


def _serialize_credential(cred: ApiCredential) -> dict:
    """Convert ApiCredential model to plain dict without SQLAlchemy state."""
    data = cred.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


class ApiCredentialCreate(BaseModel):
    name: str
    test_mode: Optional[bool] = False
    expires_at: Optional[datetime] = None
    browser_origins: Optional[List[str]] = None


class ApiCredentialUpdate(BaseModel):
    name: Optional[str] = None
    expires_at: Optional[datetime] = None
    browser_origins: Optional[List[str]] = None


class BulkDeleteRequest(BaseModel):
    ids: List[str]


class RollRequest(BaseModel):
    password: str
    expiration: Optional[datetime] = None

@router.get("/", response_model=List[dict])
def list_api_credentials(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = (
        db.query(ApiCredential)
        .filter(
            ApiCredential.company_uuid == current.company_uuid,
            ApiCredential.deleted_at.is_(None),
        )
        .offset(offset)
        .limit(limit)
    )
    credentials = query.all()
    return [_serialize_credential(c) for c in credentials]


@router.get("/export", response_model=dict)
def export_api_credentials(
    format: str = Query("xlsx", regex="^(xlsx|csv)$"),
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """
    Export API credentials summary.
    Currently returns a JSON stub with count and format to mirror Laravel's behavior
    without generating real files.
    """
    credentials = (
        db.query(ApiCredential)
        .filter(
            ApiCredential.company_uuid == current.company_uuid,
            ApiCredential.deleted_at.is_(None),
        )
        .all()
    )

    return {
        "message": "Export functionality not yet fully implemented",
        "count": len(credentials),
        "format": format,
    }


@router.get("/{id}", response_model=dict)
def get_api_credential(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    query = (
        db.query(ApiCredential)
        .filter(
            ApiCredential.company_uuid == current.company_uuid,
            ApiCredential.deleted_at.is_(None),
        )
    )

    credential = query.filter(ApiCredential.uuid == id).first()
    if not credential:
        # If id looks like an integer, try numeric primary key lookup
        try:
            numeric_id = int(id)
        except ValueError:
            numeric_id = None
        if numeric_id is not None:
            credential = query.filter(ApiCredential.id == numeric_id).first()

    if not credential:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API credential not found")
    return _serialize_credential(credential)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_api_credential(
    payload: ApiCredentialCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Generate API key and secret (simplified - in production use proper key generation)
    import hashlib
    import secrets
    seed = str(int(datetime.now(timezone.utc).timestamp())) + str(uuid.uuid4().int)
    key_hash = hashlib.sha256(seed.encode()).hexdigest()[:14]
    key_prefix = "flb_test_" if payload.test_mode else "flb_live_"
    api_key = key_prefix + key_hash
    secret = hashlib.sha256(secrets.token_urlsafe(32).encode()).hexdigest()
    
    credential = ApiCredential()
    credential.uuid = str(uuid.uuid4())
    credential.user_uuid = current.uuid
    credential.company_uuid = current.company_uuid
    credential.name = payload.name
    credential.key = api_key
    credential.secret = secret
    # Store as 0/1 integer to match schema
    credential.test_mode = 1 if payload.test_mode else 0
    credential.expires_at = payload.expires_at
    credential.browser_origins = payload.browser_origins or []
    credential.created_at = datetime.now(timezone.utc)
    credential.updated_at = datetime.now(timezone.utc)

    db.add(credential)
    db.commit()
    db.refresh(credential)
    return _serialize_credential(credential)


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_api_credential(
    id: str,
    payload: ApiCredentialUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = (
        db.query(ApiCredential)
        .filter(
            ApiCredential.company_uuid == current.company_uuid,
            ApiCredential.deleted_at.is_(None),
        )
    )
    credential = base_query.filter(ApiCredential.uuid == id).first()
    if not credential:
        try:
            numeric_id = int(id)
        except ValueError:
            numeric_id = None
        if numeric_id is not None:
            credential = base_query.filter(ApiCredential.id == numeric_id).first()
    if not credential:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API credential not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(credential, field):
            setattr(credential, field, value)
    
    credential.updated_at = datetime.now(timezone.utc)
    db.add(credential)
    db.commit()
    db.refresh(credential)
    return _serialize_credential(credential)


@router.delete("/bulk-delete", status_code=status.HTTP_200_OK)
def bulk_delete_api_credentials(
    payload: BulkDeleteRequest,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Bulk soft-delete credentials by UUID list."""
    if not payload.ids:
        return {"status": "ok", "message": "No ids provided, nothing deleted", "deleted": 0}

    credentials = (
        db.query(ApiCredential)
        .filter(
            ApiCredential.company_uuid == current.company_uuid,
            ApiCredential.deleted_at.is_(None),
            ApiCredential.uuid.in_(payload.ids),
        )
        .all()
    )

    for credential in credentials:
        credential.deleted_at = datetime.now(timezone.utc)
        db.add(credential)

    db.commit()
    return {"status": "ok", "message": f"{len(credentials)} API credentials deleted", "deleted": len(credentials)}


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_api_credential(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = (
        db.query(ApiCredential)
        .filter(
            ApiCredential.company_uuid == current.company_uuid,
            ApiCredential.deleted_at.is_(None),
        )
    )
    credential = base_query.filter(ApiCredential.uuid == id).first()
    if not credential:
        try:
            numeric_id = int(id)
        except ValueError:
            numeric_id = None
        if numeric_id is not None:
            credential = base_query.filter(ApiCredential.id == numeric_id).first()
    if not credential:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API credential not found")

    credential.deleted_at = datetime.now(timezone.utc)
    db.add(credential)
    db.commit()
    return {"status": "ok", "message": "API credential deleted"}


@router.patch("/roll/{id}", response_model=dict)
def roll_api_credential(
    id: str,
    payload: RollRequest,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Verify password
    from app.core.security import verify_password
    if not verify_password(payload.password, current.password or ""):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required to roll key failed")
    
    base_query = (
        db.query(ApiCredential)
        .filter(
            ApiCredential.company_uuid == current.company_uuid,
            ApiCredential.deleted_at.is_(None),
        )
    )
    credential = base_query.filter(ApiCredential.uuid == id).first()
    if not credential:
        try:
            numeric_id = int(id)
        except ValueError:
            numeric_id = None
        if numeric_id is not None:
            credential = base_query.filter(ApiCredential.id == numeric_id).first()
    if not credential:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API credential not found")
    
    # Generate new key
    import hashlib
    import secrets
    seed = str(int(datetime.now(timezone.utc).timestamp())) + str(credential.id)
    key_hash = hashlib.sha256(seed.encode()).hexdigest()[:14]
    key_prefix = "flb_test_" if credential.test_mode else "flb_live_"
    new_key = key_prefix + key_hash
    new_secret = hashlib.sha256(secrets.token_urlsafe(32).encode()).hexdigest()
    
    credential.key = new_key
    credential.secret = new_secret
    if payload.expiration:
        credential.expires_at = payload.expiration
    credential.updated_at = datetime.now(timezone.utc)
    
    db.add(credential)
    db.commit()
    db.refresh(credential)
    return _serialize_credential(credential)


@router.get("/export", response_model=dict)
def export_api_credentials(
    format: str = Query("xlsx", regex="^(xlsx|csv)$"),
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Export API credentials summary (stub)."""
    credentials = (
        db.query(ApiCredential)
        .filter(
            ApiCredential.company_uuid == current.company_uuid,
            ApiCredential.deleted_at.is_(None),
        )
        .all()
    )

    return {
        "message": "Export functionality not yet fully implemented",
        "count": len(credentials),
        "format": format,
    }

