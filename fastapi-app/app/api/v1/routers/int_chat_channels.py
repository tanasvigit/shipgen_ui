from typing import List, Optional, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.chat_channel import ChatChannel
from app.models.chat_participant import ChatParticipant
from app.models.chat_message import ChatMessage
from app.models.chat_receipt import ChatReceipt
from app.models.user import User

router = APIRouter(prefix="/int/v1/chat-channels", tags=["int-chat-channels"])


class ChatChannelCreate(BaseModel):
    name: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class ChatChannelUpdate(BaseModel):
    name: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


def _channel_to_dict(channel: ChatChannel) -> dict:
    """Convert ChatChannel ORM instance to a JSON-serializable dict (avoids InstanceState)."""
    return {
        "id": channel.id,
        "uuid": channel.uuid,
        "public_id": channel.public_id,
        "company_uuid": channel.company_uuid,
        "created_by_uuid": channel.created_by_uuid,
        "name": channel.name,
        "slug": channel.slug,
        "meta": channel.meta,
        "deleted_at": channel.deleted_at.isoformat() if channel.deleted_at else None,
        "created_at": channel.created_at.isoformat() if channel.created_at else None,
        "updated_at": channel.updated_at.isoformat() if channel.updated_at else None,
    }


@router.get("/", response_model=List[dict])
def list_chat_channels(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    channels = db.query(ChatChannel).filter(
        ChatChannel.company_uuid == current.company_uuid,
        ChatChannel.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [_channel_to_dict(ch) for ch in channels]


@router.get("/unread-count/{channel_id}", response_model=dict)
def get_unread_count_for_channel(
    channel_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Get unread message count for a specific channel."""
    channel = db.query(ChatChannel).filter(
        ChatChannel.company_uuid == current.company_uuid,
        (ChatChannel.uuid == channel_id) | (ChatChannel.public_id == channel_id),
        ChatChannel.deleted_at.is_(None)
    ).first()
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.chat_channel_uuid == channel.uuid,
        ChatParticipant.user_uuid == current.uuid,
        ChatParticipant.deleted_at.is_(None)
    ).first()
    if not participant:
        return {"unread_count": 0, "channel_id": channel_id}
    total_messages = db.query(ChatMessage).filter(
        ChatMessage.chat_channel_uuid == channel.uuid,
        ChatMessage.sender_uuid != current.uuid,
        ChatMessage.deleted_at.is_(None)
    ).count()
    read_messages = db.query(ChatReceipt).filter(
        ChatReceipt.participant_uuid == participant.uuid,
        ChatReceipt.read_at.isnot(None)
    ).count()
    unread_count = max(0, total_messages - read_messages)
    return {"unread_count": unread_count, "channel_id": channel_id}


@router.get("/unread-count", response_model=dict)
def get_unread_count(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Get total unread message count across all channels."""
    participants = db.query(ChatParticipant).filter(
        ChatParticipant.user_uuid == current.uuid,
        ChatParticipant.deleted_at.is_(None)
    ).all()
    total_unread = 0
    for participant in participants:
        channel = db.query(ChatChannel).filter(
            ChatChannel.uuid == participant.chat_channel_uuid,
            ChatChannel.deleted_at.is_(None)
        ).first()
        if not channel:
            continue
        total_messages = db.query(ChatMessage).filter(
            ChatMessage.chat_channel_uuid == channel.uuid,
            ChatMessage.sender_uuid != current.uuid,
            ChatMessage.deleted_at.is_(None)
        ).count()
        read_messages = db.query(ChatReceipt).filter(
            ChatReceipt.participant_uuid == participant.uuid,
            ChatReceipt.read_at.isnot(None)
        ).count()
        total_unread += max(0, total_messages - read_messages)
    return {"unread_count": total_unread}


@router.get("/{id}", response_model=dict)
def get_chat_channel(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    channel = db.query(ChatChannel).filter(
        ChatChannel.company_uuid == current.company_uuid,
        (ChatChannel.uuid == id) | (ChatChannel.public_id == id),
        ChatChannel.deleted_at.is_(None)
    ).first()
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat channel not found")
    return _channel_to_dict(channel)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_chat_channel(
    payload: ChatChannelCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    channel = ChatChannel()
    channel.uuid = str(uuid.uuid4())
    channel.company_uuid = current.company_uuid
    channel.created_by_uuid = current.uuid
    channel.name = payload.name
    channel.meta = payload.meta
    
    db.add(channel)
    db.commit()
    db.refresh(channel)
    
    # Create participant for creator
    participant = ChatParticipant()
    participant.uuid = str(uuid.uuid4())
    participant.company_uuid = current.company_uuid
    participant.chat_channel_uuid = channel.uuid
    participant.user_uuid = current.uuid
    db.add(participant)
    db.commit()
    
    return _channel_to_dict(channel)


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_chat_channel(
    id: str,
    payload: ChatChannelUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    channel = db.query(ChatChannel).filter(
        ChatChannel.company_uuid == current.company_uuid,
        (ChatChannel.uuid == id) | (ChatChannel.public_id == id),
        ChatChannel.deleted_at.is_(None)
    ).first()
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat channel not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(channel, field):
            setattr(channel, field, value)
    
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return _channel_to_dict(channel)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_chat_channel(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    channel = db.query(ChatChannel).filter(
        ChatChannel.company_uuid == current.company_uuid,
        (ChatChannel.uuid == id) | (ChatChannel.public_id == id),
        ChatChannel.deleted_at.is_(None)
    ).first()
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat channel not found")
    
    channel.deleted_at = datetime.utcnow()
    db.add(channel)
    db.commit()
    return _channel_to_dict(channel)

