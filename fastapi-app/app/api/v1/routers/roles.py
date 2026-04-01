from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.authz import require_permission
from app.core.database import get_db
from app.models.role import Role
from app.schemas.iam import RoleCreate, RoleOut, RoleUpdate

router = APIRouter(prefix="/int/v1/roles", tags=["roles"])


@router.get("/", response_model=List[RoleOut])
def list_roles(
    db: Session = Depends(get_db),
    _user=Depends(require_permission("roles.view")),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return db.query(Role).offset(offset).limit(limit).all()


@router.post("/", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_permission("roles.create")),
):
    if db.query(Role).filter(Role.name == payload.name, Role.guard_name == payload.guard_name).first():
        raise HTTPException(status_code=400, detail="Role with this name and guard already exists.")

    role = Role(
        id=str(uuid.uuid4()),
        name=payload.name,
        guard_name=payload.guard_name,
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.get("/{role_id}", response_model=RoleOut)
def get_role(
    role_id: str,
    db: Session = Depends(get_db),
    _user=Depends(require_permission("roles.view")),
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")
    return role


@router.patch("/{role_id}", response_model=RoleOut)
def update_role(
    role_id: str,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_permission("roles.update")),
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")

    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(role, field, value)

    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: str,
    db: Session = Depends(get_db),
    _user=Depends(require_permission("roles.delete")),
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")

    db.delete(role)
    db.commit()



