from typing import List, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_review import StorefrontReview
from app.models.user import User

router = APIRouter(prefix="/int/v1/reviews", tags=["int-storefront-reviews"])


class ReviewCreate(BaseModel):
    subject_uuid: str
    subject_type: str
    customer_uuid: Optional[str] = None
    rating: int
    content: Optional[str] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    content: Optional[str] = None


@router.get("/", response_model=List[dict])
def list_reviews(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    reviews = db.query(StorefrontReview).filter(
        StorefrontReview.company_uuid == current.company_uuid,
        StorefrontReview.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [r.__dict__ for r in reviews]


@router.get("/{id}", response_model=dict)
def get_review(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    review = db.query(StorefrontReview).filter(
        StorefrontReview.company_uuid == current.company_uuid,
        (StorefrontReview.uuid == id) | (StorefrontReview.public_id == id),
        StorefrontReview.deleted_at.is_(None)
    ).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return review.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    review = StorefrontReview()
    review.uuid = str(uuid.uuid4())
    review.company_uuid = current.company_uuid
    review.created_by_uuid = current.uuid
    review.subject_uuid = payload.subject_uuid
    review.subject_type = payload.subject_type
    review.customer_uuid = payload.customer_uuid
    review.rating = payload.rating
    review.content = payload.content
    
    db.add(review)
    db.commit()
    db.refresh(review)
    return review.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_review(
    id: str,
    payload: ReviewUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    review = db.query(StorefrontReview).filter(
        StorefrontReview.company_uuid == current.company_uuid,
        (StorefrontReview.uuid == id) | (StorefrontReview.public_id == id),
        StorefrontReview.deleted_at.is_(None)
    ).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(review, field):
            setattr(review, field, value)
    
    db.add(review)
    db.commit()
    db.refresh(review)
    return review.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_review(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    review = db.query(StorefrontReview).filter(
        StorefrontReview.company_uuid == current.company_uuid,
        (StorefrontReview.uuid == id) | (StorefrontReview.public_id == id),
        StorefrontReview.deleted_at.is_(None)
    ).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    review.deleted_at = datetime.utcnow()
    db.add(review)
    db.commit()
    return review.__dict__

