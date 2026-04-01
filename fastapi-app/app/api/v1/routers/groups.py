import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.group import Group
from app.models.group_user import GroupUser
from app.models.user import User

router = APIRouter(prefix="/int/v1/groups", tags=["groups"])


class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


@router.get("/", response_model=List[dict])
def list_groups(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(Group).filter(
        Group.company_uuid == current.company_uuid,
        Group.deleted_at.is_(None)
    )
    groups = query.offset(offset).limit(limit).all()
    return [g.__dict__ for g in groups]


@router.get("/{id}", response_model=dict)
def get_group(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    group = db.query(Group).filter(
        (Group.uuid == id) | (Group.public_id == id) | (Group.slug == id),
        Group.company_uuid == current.company_uuid,
        Group.deleted_at.is_(None)
    ).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_group(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    import re
    group = Group()
    group.uuid = str(uuid.uuid4())
    group.company_uuid = current.company_uuid
    group.name = payload.name
    group.description = payload.description
    # Simple slug generation
    group.slug = re.sub(r'[^\w\s-]', '', payload.name.lower()).strip().replace(' ', '-')
    group.created_at = datetime.now(timezone.utc)
    group.updated_at = datetime.now(timezone.utc)
    
    db.add(group)
    db.commit()
    db.refresh(group)
    return group.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_group(
    id: str,
    payload: GroupUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    import re
    group = db.query(Group).filter(
        (Group.uuid == id) | (Group.public_id == id),
        Group.company_uuid == current.company_uuid,
        Group.deleted_at.is_(None)
    ).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    
    if payload.name:
        group.name = payload.name
        # Simple slug generation
        group.slug = re.sub(r'[^\w\s-]', '', payload.name.lower()).strip().replace(' ', '-')
    if payload.description is not None:
        group.description = payload.description
    
    group.updated_at = datetime.now(timezone.utc)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_group(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    group = db.query(Group).filter(
        (Group.uuid == id) | (Group.public_id == id),
        Group.company_uuid == current.company_uuid,
        Group.deleted_at.is_(None)
    ).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    
    group.deleted_at = datetime.now(timezone.utc)
    db.add(group)
    db.commit()
    return {"status": "ok", "message": "Group deleted"}


@router.post("/{id}/users/{user_uuid}", response_model=dict)
def add_user_to_group(
    id: str,
    user_uuid: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    group = db.query(Group).filter(
        (Group.uuid == id) | (Group.public_id == id),
        Group.company_uuid == current.company_uuid,
        Group.deleted_at.is_(None)
    ).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    
    # Check if user is already in group
    existing = db.query(GroupUser).filter(
        GroupUser.group_uuid == group.uuid,
        GroupUser.user_uuid == user_uuid
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already in group")
    
    group_user = GroupUser()
    group_user.uuid = str(uuid.uuid4())
    group_user.company_uuid = current.company_uuid
    group_user.group_uuid = group.uuid
    group_user.user_uuid = user_uuid
    group_user.created_at = datetime.now(timezone.utc)
    group_user.updated_at = datetime.now(timezone.utc)
    
    db.add(group_user)
    db.commit()
    db.refresh(group_user)
    return group_user.__dict__


@router.delete("/{id}/users/{user_uuid}", status_code=status.HTTP_200_OK)
def remove_user_from_group(
    id: str,
    user_uuid: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    group = db.query(Group).filter(
        (Group.uuid == id) | (Group.public_id == id),
        Group.company_uuid == current.company_uuid,
        Group.deleted_at.is_(None)
    ).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    
    group_user = db.query(GroupUser).filter(
        GroupUser.group_uuid == group.uuid,
        GroupUser.user_uuid == user_uuid
    ).first()
    if not group_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not in group")
    
    db.delete(group_user)
    db.commit()
    return {"status": "ok", "message": "User removed from group"}

