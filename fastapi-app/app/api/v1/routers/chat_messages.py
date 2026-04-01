from typing import List, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.chat_message import ChatMessage
from app.models.chat_channel import ChatChannel
from app.models.chat_participant import ChatParticipant
from app.models.user import User

router = APIRouter(prefix="/int/v1/chat-messages", tags=["chat-messages"])


class ChatMessageCreate(BaseModel):
    chat_channel_uuid: str
    content: str


class ChatMessageUpdate(BaseModel):
    content: Optional[str] = None


@router.get("/", response_model=List[dict])
def list_chat_messages(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    chat_channel_uuid: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(ChatMessage).filter(
        ChatMessage.company_uuid == current.company_uuid,
        ChatMessage.deleted_at.is_(None)
    )
    
    if chat_channel_uuid:
        query = query.filter(ChatMessage.chat_channel_uuid == chat_channel_uuid)
    
    messages = query.order_by(ChatMessage.created_at.desc()).offset(offset).limit(limit).all()
    return [m.__dict__ for m in messages]


@router.get("/{id}", response_model=dict)
def get_chat_message(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    message = db.query(ChatMessage).filter(
        ChatMessage.company_uuid == current.company_uuid,
        (ChatMessage.uuid == id) | (ChatMessage.public_id == id),
        ChatMessage.deleted_at.is_(None)
    ).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat message not found")
    return message.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_chat_message(
    payload: ChatMessageCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Get or create participant
    from app.models.chat_participant import ChatParticipant
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.chat_channel_uuid == payload.chat_channel_uuid,
        ChatParticipant.user_uuid == current.uuid,
        ChatParticipant.deleted_at.is_(None)
    ).first()
    
    if not participant:
        participant = ChatParticipant()
        participant.uuid = str(uuid.uuid4())
        participant.company_uuid = current.company_uuid
        participant.chat_channel_uuid = payload.chat_channel_uuid
        participant.user_uuid = current.uuid
        db.add(participant)
        db.commit()
        db.refresh(participant)
    
    message = ChatMessage()
    message.uuid = str(uuid.uuid4())
    message.company_uuid = current.company_uuid
    message.chat_channel_uuid = payload.chat_channel_uuid
    message.sender_uuid = participant.uuid
    message.content = payload.content
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Notify other participants
    from app.models.user_device import UserDevice
    from app.utils.push_notifications import push_service
    
    # Get participants (excluding sender)
    participants = db.query(ChatParticipant).filter(
        ChatParticipant.chat_channel_uuid == message.chat_channel_uuid,
        ChatParticipant.user_uuid != current.uuid,  # Don't notify sender
        ChatParticipant.deleted_at.is_(None)
    ).all()
    
    # Get device tokens for participants
    device_tokens = []
    for participant in participants:
        devices = db.query(UserDevice).filter(
            UserDevice.user_uuid == participant.user_uuid,
            UserDevice.deleted_at.is_(None)
        ).all()
        for device in devices:
            if device.token:
                device_tokens.append(device.token)
    
    # Send push notifications
    if device_tokens:
        channel = db.query(ChatChannel).filter(
            ChatChannel.uuid == message.chat_channel_uuid
        ).first()
        channel_name = channel.name if channel else "Chat"
        
        push_service.send_to_devices(
            registration_ids=device_tokens,
            title=f"New message in {channel_name}",
            body=payload.content[:100],  # Truncate long messages
            data={
                "type": "chat_message",
                "channel_id": channel.public_id if channel else None,
                "message_id": message.public_id
            }
        )
    
    return message.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_chat_message(
    id: str,
    payload: ChatMessageUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    message = db.query(ChatMessage).filter(
        ChatMessage.company_uuid == current.company_uuid,
        (ChatMessage.uuid == id) | (ChatMessage.public_id == id),
        ChatMessage.deleted_at.is_(None)
    ).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat message not found")
    
    # Check if user is the sender
    from app.models.chat_participant import ChatParticipant
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.uuid == message.sender_uuid,
        ChatParticipant.user_uuid == current.uuid
    ).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this message")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(message, field):
            setattr(message, field, value)
    
    db.add(message)
    db.commit()
    db.refresh(message)
    return message.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_chat_message(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    message = db.query(ChatMessage).filter(
        ChatMessage.company_uuid == current.company_uuid,
        (ChatMessage.uuid == id) | (ChatMessage.public_id == id),
        ChatMessage.deleted_at.is_(None)
    ).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat message not found")
    
    # Check if user is the sender
    from app.models.chat_participant import ChatParticipant
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.uuid == message.sender_uuid,
        ChatParticipant.user_uuid == current.uuid
    ).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this message")
    
    message.deleted_at = datetime.utcnow()
    db.add(message)
    db.commit()
    return message.__dict__

