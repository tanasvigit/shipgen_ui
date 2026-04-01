from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: str
    type: str
    notifiable_type: str
    notifiable_id: str
    data: Any
    read_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class NotificationSettings(BaseModel):
    # free-form company-level settings map
    notificationSettings: dict[str, Any]


class MarkAsReadRequest(BaseModel):
    notifications: list[str]


class BulkDeleteRequest(BaseModel):
    notifications: Optional[list[str]] = None



