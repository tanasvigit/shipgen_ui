from typing import List, Optional, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.comment import Comment
from app.models.user import User

router = APIRouter(prefix="/int/v1/comments", tags=["int-comments"])


def _serialize_comment(comment: Comment) -> dict:
    """Convert Comment model to plain dict without SQLAlchemy state."""
    data = comment.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


class CommentCreate(BaseModel):
    subject_uuid: str
    subject_type: str
    content: str
    parent_comment_uuid: Optional[str] = None
    tags: Optional[list[str]] = None
    meta: Optional[dict[str, Any]] = None


class CommentUpdate(BaseModel):
    content: Optional[str] = None
    tags: Optional[list[str]] = None
    meta: Optional[dict[str, Any]] = None


@router.get("/", response_model=List[dict])
def list_comments(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    subject_uuid: Optional[str] = Query(None),
    subject_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(Comment).filter(
        Comment.company_uuid == current.company_uuid,
        Comment.deleted_at.is_(None),
    )

    if subject_uuid:
        query = query.filter(Comment.subject_uuid == subject_uuid)
    if subject_type:
        query = query.filter(Comment.subject_type == subject_type)

    comments = query.offset(offset).limit(limit).all()
    return [_serialize_comment(c) for c in comments]


@router.get("/{id}", response_model=dict)
def get_comment(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    comment = (
        db.query(Comment)
        .filter(
            Comment.company_uuid == current.company_uuid,
            (Comment.uuid == id) | (Comment.public_id == id),
            Comment.deleted_at.is_(None),
        )
        .first()
    )
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return _serialize_comment(comment)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_comment(
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    comment = Comment()
    comment.uuid = str(uuid.uuid4())
    comment.company_uuid = current.company_uuid
    comment.author_uuid = current.uuid
    comment.subject_uuid = payload.subject_uuid
    comment.subject_type = payload.subject_type
    comment.parent_comment_uuid = payload.parent_comment_uuid
    comment.content = payload.content
    comment.tags = payload.tags
    comment.meta = payload.meta

    db.add(comment)
    db.commit()
    db.refresh(comment)
    return _serialize_comment(comment)


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_comment(
    id: str,
    payload: CommentUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    comment = (
        db.query(Comment)
        .filter(
            Comment.company_uuid == current.company_uuid,
            (Comment.uuid == id) | (Comment.public_id == id),
            Comment.deleted_at.is_(None),
        )
        .first()
    )
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(comment, field):
            setattr(comment, field, value)

    db.add(comment)
    db.commit()
    db.refresh(comment)
    return _serialize_comment(comment)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_comment(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    comment = (
        db.query(Comment)
        .filter(
            Comment.company_uuid == current.company_uuid,
            (Comment.uuid == id) | (Comment.public_id == id),
            Comment.deleted_at.is_(None),
        )
        .first()
    )
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    comment.deleted_at = datetime.utcnow()
    db.add(comment)
    db.commit()
    return {"status": "ok", "message": "Comment deleted successfully."}

