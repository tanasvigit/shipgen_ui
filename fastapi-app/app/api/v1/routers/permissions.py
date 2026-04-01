from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.authz import require_permission
from app.core.database import get_db
from app.models.permission import Permission
from app.schemas.iam import PermissionCreate, PermissionOut, PermissionUpdate

router = APIRouter(prefix="/int/v1/permissions", tags=["permissions"])


@router.get("/", response_model=List[PermissionOut])
def list_permissions(
    db: Session = Depends(get_db),
    _user=Depends(require_permission("permissions.view")),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return db.query(Permission).offset(offset).limit(limit).all()


@router.post("/", response_model=PermissionOut, status_code=status.HTTP_201_CREATED)
def create_permission(
    payload: PermissionCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_permission("permissions.create")),
):
    if db.query(Permission).filter(
        Permission.name == payload.name,
        Permission.guard_name == payload.guard_name,
    ).first():
        raise HTTPException(status_code=400, detail="Permission with this name and guard already exists.")

    perm = Permission(
        id=str(uuid.uuid4()),
        name=payload.name,
        guard_name=payload.guard_name,
    )
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm


@router.get("/{permission_id}", response_model=PermissionOut)
def get_permission(
    permission_id: str,
    db: Session = Depends(get_db),
    _user=Depends(require_permission("permissions.view")),
):
    perm = db.query(Permission).filter(Permission.id == permission_id).first()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found.")
    return perm


@router.patch("/{permission_id}", response_model=PermissionOut)
def update_permission(
    permission_id: str,
    payload: PermissionUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_permission("permissions.update")),
):
    perm = db.query(Permission).filter(Permission.id == permission_id).first()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found.")

    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(perm, field, value)

    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    permission_id: str,
    db: Session = Depends(get_db),
    _user=Depends(require_permission("permissions.delete")),
):
    perm = db.query(Permission).filter(Permission.id == permission_id).first()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found.")

    db.delete(perm)
    db.commit()



