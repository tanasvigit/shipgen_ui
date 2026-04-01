from typing import Any, List, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_review import StorefrontReview
from app.models.storefront_store import StorefrontStore
from app.models.user import User
from app.schemas.storefront_review import ReviewCreate, ReviewOut

router = APIRouter(prefix="/storefront/v1/reviews", tags=["storefront-reviews"])


@router.get("/", response_model=List[ReviewOut])
def list_reviews(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(None, ge=1, le=100),
    offset: int = Query(None, ge=0),
    sort: Optional[str] = None,
    store: Optional[str] = None,
):
    # Get storefront_store or storefront_network from session (simplified)
    # In production, this would come from session/headers
    query = db.query(StorefrontReview)
    
    if store:
        store_obj = (
            db.query(StorefrontStore)
            .filter(StorefrontStore.company_uuid == current.company_uuid, (StorefrontStore.uuid == store) | (StorefrontStore.public_id == store))
            .first()
        )
        if store_obj:
            query = query.filter(StorefrontReview.subject_uuid == store_obj.uuid)
    
    # Apply sorting
    if sort:
        if sort in ["highest", "highest rated"]:
            query = query.order_by(StorefrontReview.rating.desc())
        elif sort in ["lowest", "lowest rated"]:
            query = query.order_by(StorefrontReview.rating.asc())
        elif sort in ["newest", "newest first"]:
            query = query.order_by(StorefrontReview.created_at.desc())
        elif sort in ["oldest", "oldest first"]:
            query = query.order_by(StorefrontReview.created_at.asc())
    
    if limit:
        query = query.limit(limit)
    if offset:
        query = query.offset(offset)
    
    reviews = query.all()
    return reviews


@router.get("/count", response_model=dict)
def count_reviews(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    store: Optional[str] = None,
):
    counts = {}
    store_obj = None
    
    if store:
        store_obj = (
            db.query(StorefrontStore)
            .filter(StorefrontStore.company_uuid == current.company_uuid, (StorefrontStore.uuid == store) | (StorefrontStore.public_id == store))
            .first()
        )
    
    for rating in range(1, 6):
        query = db.query(StorefrontReview).filter(StorefrontReview.rating == rating)
        if store_obj:
            query = query.filter(StorefrontReview.subject_uuid == store_obj.uuid)
        counts[rating] = query.count()
    
    return counts


@router.get("/{id}", response_model=ReviewOut)
def get_review(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    review = (
        db.query(StorefrontReview)
        .filter((StorefrontReview.uuid == id) | (StorefrontReview.public_id == id))
        .first()
    )
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    return review


@router.post("/", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Resolve subject (store or product)
    # Simplified - in production, use Utils.resolveSubject
    subject = None
    # Try to find as store
    subject = (
        db.query(StorefrontStore)
        .filter(StorefrontStore.company_uuid == current.company_uuid, (StorefrontStore.uuid == payload.subject) | (StorefrontStore.public_id == payload.subject))
        .first()
    )
    
    if not subject:
        # Try to find as product
        from app.models.storefront_product import StorefrontProduct
        subject = (
            db.query(StorefrontProduct)
            .filter(StorefrontProduct.company_uuid == current.company_uuid, (StorefrontProduct.uuid == payload.subject) | (StorefrontProduct.public_id == payload.subject))
            .first()
        )
    
    if not subject:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid subject for review")
    
    # Get customer from token (simplified)
    from app.models.contact import Contact
    customer = (
        db.query(Contact)
        .filter(Contact.company_uuid == current.company_uuid, Contact.user_uuid == current.uuid)
        .first()
    )
    
    if not customer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create reviews")
    
    review = StorefrontReview()
    review.uuid = str(uuid.uuid4())
    review.created_by_uuid = current.uuid
    review.customer_uuid = customer.uuid
    review.subject_uuid = subject.uuid
    review.subject_type = "Store" if isinstance(subject, StorefrontStore) else "Product"
    review.rating = payload.rating
    review.content = payload.content
    
    # Handle file uploads (simplified - in production, handle base64 uploads)
    
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_review(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    review = (
        db.query(StorefrontReview)
        .filter((StorefrontReview.uuid == id) | (StorefrontReview.public_id == id))
        .first()
    )
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    
    review.deleted_at = datetime.utcnow()
    db.add(review)
    db.commit()
    return review

