from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.category import Category
from app.models.storefront_store import StorefrontStore
from app.models.storefront_network import StorefrontNetwork
from app.models.user import User
from app.schemas.category import CategoryOut

router = APIRouter(prefix="/storefront/v1/categories", tags=["storefront-categories"])


@router.get("/", response_model=List[CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    parents_only: bool = Query(False),
    parent: Optional[str] = None,
    with_products: bool = Query(False),
    with_stores: bool = Query(False),
    store: Optional[str] = None,
):
    query = db.query(Category)
    
    # Determine owner (store or network)
    owner_uuid = None
    for_field = "storefront_product"
    
    if store:
        store_obj = (
            db.query(StorefrontStore)
            .filter(StorefrontStore.company_uuid == current.company_uuid, (StorefrontStore.uuid == store) | (StorefrontStore.public_id == store))
            .first()
        )
        if store_obj:
            owner_uuid = store_obj.uuid
    # In production, would also check session('storefront_store') or session('storefront_network')
    
    if owner_uuid:
        query = query.filter(Category.owner_uuid == owner_uuid, Category.for_field == for_field)
    
    if parents_only:
        query = query.filter(Category.parent_uuid.is_(None))
    
    if parent:
        parent_cat = (
            db.query(Category)
            .filter((Category.uuid == parent) | (Category.public_id == parent))
            .first()
        )
        if parent_cat:
            query = query.filter(Category.parent_uuid == parent_cat.uuid)
    
    categories = query.all()
    
    # Add products if requested
    if with_products:
        from app.models.storefront_product import StorefrontProduct
        category_ids = [cat.uuid for cat in categories]
        products = (
            db.query(StorefrontProduct)
            .filter(StorefrontProduct.category_uuid.in_(category_ids), StorefrontProduct.is_available == True)
            .all()
        )
        # Group products by category
        products_by_category = {}
        for product in products:
            if product.category_uuid not in products_by_category:
                products_by_category[product.category_uuid] = []
            products_by_category[product.category_uuid].append(product)
        
        # Add products to categories
        for cat in categories:
            cat.products = products_by_category.get(cat.uuid, [])
    
    # Add stores if requested
    if with_stores:
        from app.models.storefront_network_store import StorefrontNetworkStore
        category_ids = [cat.uuid for cat in categories]
        network_stores = (
            db.query(StorefrontNetworkStore)
            .filter(StorefrontNetworkStore.category_uuid.in_(category_ids))
            .all()
        )
        # Group stores by category
        stores_by_category = {}
        for ns in network_stores:
            if ns.category_uuid not in stores_by_category:
                stores_by_category[ns.category_uuid] = []
            store = (
                db.query(StorefrontStore)
                .filter(StorefrontStore.uuid == ns.store_uuid)
                .first()
            )
            if store:
                stores_by_category[ns.category_uuid].append(store)
        
        # Add stores to categories
        for cat in categories:
            cat.stores = stores_by_category.get(cat.uuid, [])
    
    return categories

