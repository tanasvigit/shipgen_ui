from fastapi import APIRouter, Depends

from app.api.v1.routers.auth import _get_current_user
from app.models.user import User
from app.schemas.auth import MeUser


router = APIRouter(prefix="/int/v1", tags=["auth"])


@router.get("/me", response_model=MeUser)
def current_user_me(
    current: User = Depends(_get_current_user),
) -> MeUser:
    """
    /int/v1/me endpoint for Ember console.

    Returns the authenticated user in the shape:
    {
      "id": "<string>",
      "uuid": "<string>",
      "email": "<user_email>",
      "name": "<user_name>",
      "type": "<string>"
    }
    """
    user_id = current.uuid or str(current.id)
    return MeUser(
        id=user_id,
        uuid=user_id,
        email=current.email,
        name=current.name,
        type=current.type,
    )

