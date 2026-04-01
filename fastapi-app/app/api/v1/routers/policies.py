from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.authz import require_permission
from app.core.database import get_db
from app.models.policy import Policy
from app.models.user import User
from app.schemas.iam import PolicyCreate, PolicyOut, PolicyUpdate
from app.api.v1.routers.auth import _get_current_user

router = APIRouter(prefix="/int/v1/policies", tags=["policies"])


@router.get("/", response_model=List[PolicyOut])
def list_policies(
    db: Session = Depends(get_db),
    _user=Depends(require_permission("policies.view")),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return db.query(Policy).offset(offset).limit(limit).all()


@router.post("/", response_model=PolicyOut, status_code=status.HTTP_201_CREATED)
def create_policy(
    payload: PolicyCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    _user2=Depends(require_permission("policies.create")),
):
    policy = Policy(
        id=str(uuid.uuid4()),
        company_uuid=payload.company_uuid or current.company_uuid,
        name=payload.name,
        guard_name=payload.guard_name,
        description=payload.description,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.get("/{policy_id}", response_model=PolicyOut)
def get_policy(
    policy_id: str,
    db: Session = Depends(get_db),
    _user=Depends(require_permission("policies.view")),
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found.")
    return policy


@router.patch("/{policy_id}", response_model=PolicyOut)
def update_policy(
    policy_id: str,
    payload: PolicyUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_permission("policies.update")),
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found.")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(policy, field, value)

    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(
    policy_id: str,
    db: Session = Depends(get_db),
    _user=Depends(require_permission("policies.delete")),
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found.")

    db.delete(policy)
    db.commit()



