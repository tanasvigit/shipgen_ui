from typing import List, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_vote import StorefrontVote
from app.models.user import User

router = APIRouter(prefix="/int/v1/votes", tags=["int-storefront-votes"])


class VoteCreate(BaseModel):
    customer_uuid: str
    subject_uuid: str
    subject_type: str
    type: str


class VoteUpdate(BaseModel):
    customer_uuid: Optional[str] = None
    subject_uuid: Optional[str] = None
    subject_type: Optional[str] = None
    type: Optional[str] = None


@router.get("/", response_model=List[dict])
def list_votes(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    votes = db.query(StorefrontVote).filter(
        StorefrontVote.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [vote.__dict__ for vote in votes]


@router.get("/{id}", response_model=dict)
def get_vote(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    vote = db.query(StorefrontVote).filter(
        (StorefrontVote.uuid == id) | (StorefrontVote.public_id == id),
        StorefrontVote.deleted_at.is_(None)
    ).first()
    if not vote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote not found")
    return vote.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_vote(
    payload: VoteCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    vote = StorefrontVote()
    vote.uuid = str(uuid.uuid4())
    vote.created_by_uuid = current.uuid
    vote.customer_uuid = payload.customer_uuid
    vote.subject_uuid = payload.subject_uuid
    vote.subject_type = payload.subject_type
    vote.type = payload.type
    
    db.add(vote)
    db.commit()
    db.refresh(vote)
    return vote.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_vote(
    id: str,
    payload: VoteUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    vote = db.query(StorefrontVote).filter(
        (StorefrontVote.uuid == id) | (StorefrontVote.public_id == id),
        StorefrontVote.deleted_at.is_(None)
    ).first()
    if not vote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(vote, field):
            setattr(vote, field, value)
    
    db.add(vote)
    db.commit()
    db.refresh(vote)
    return vote.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_vote(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    vote = db.query(StorefrontVote).filter(
        (StorefrontVote.uuid == id) | (StorefrontVote.public_id == id),
        StorefrontVote.deleted_at.is_(None)
    ).first()
    if not vote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote not found")
    
    vote.deleted_at = datetime.utcnow()
    db.add(vote)
    db.commit()
    return vote.__dict__

