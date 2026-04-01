from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.extension import Extension
from app.models.extension_install import ExtensionInstall
from app.models.user import User

router = APIRouter(prefix="/~registry/v1", tags=["registry"])


@router.get("/engines", response_model=List[dict])
def get_installed_engines(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """
    Retrieve a list of installed engines for the current company session.
    
    Returns a list of installed extension engines with their package.json metadata.
    """
    if not current.company_uuid:
        return []
    
    # Get all extensions installed for the current company
    installed_extensions = (
        db.query(Extension)
        .join(ExtensionInstall, Extension.uuid == ExtensionInstall.extension_uuid)
        .filter(ExtensionInstall.company_uuid == current.company_uuid)
        .filter(ExtensionInstall.deleted_at.is_(None))
        .all()
    )
    
    # Extract package.json metadata from each extension
    engines = []
    for extension in installed_extensions:
        # Get package.json from extension meta if available
        if extension.meta and isinstance(extension.meta, dict):
            package_json = extension.meta.get("package.json", {})
            if package_json:
                engines.append(package_json)
    
    return engines

