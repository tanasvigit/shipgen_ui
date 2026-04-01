from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.api.v1.routers.auth import _get_current_user


def require_role(role_name: str):
    def dependency(
        current_user: User = Depends(_get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        # Simple check: user.type or a future user_roles table can be inspected here.
        if current_user.type == role_name:
            return current_user

        # Fallback: check model_has_roles by user uuid
        exists = (
            db.execute(
                """
                SELECT 1
                FROM model_has_roles mhr
                JOIN roles r ON r.id = mhr.role_id
                WHERE mhr.model_uuid = :uuid AND r.name = :name
                """,
                {"uuid": current_user.uuid, "name": role_name},
            )
            .first()
            is not None
        )
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required role: {role_name}",
            )
        return current_user

    return dependency


def require_permission(permission_name: str):
    def dependency(
        current_user: User = Depends(_get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        # Check direct model_has_permissions
        has_direct = (
            db.execute(
                """
                SELECT 1
                FROM model_has_permissions mhp
                JOIN permissions p ON p.id = mhp.permission_id
                WHERE mhp.model_uuid = :uuid AND p.name = :name
                """,
                {"uuid": current_user.uuid, "name": permission_name},
            )
            .first()
            is not None
        )
        if has_direct:
            return current_user

        # Check via roles: model_has_roles -> role_has_permissions -> permissions
        has_via_role = (
            db.execute(
                """
                SELECT 1
                FROM model_has_roles mhr
                JOIN role_has_permissions rhp ON rhp.role_id = mhr.role_id
                JOIN permissions p ON p.id = rhp.permission_id
                WHERE mhr.model_uuid = :uuid AND p.name = :name
                """,
                {"uuid": current_user.uuid, "name": permission_name},
            )
            .first()
            is not None
        )
        if not has_via_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission_name}",
            )
        return current_user

    return dependency



