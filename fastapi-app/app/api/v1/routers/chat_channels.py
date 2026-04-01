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
from app.models.user import User

router = APIRouter(prefix="/v1/chat-channels", tags=["chat-channels"])


class ChatChannelCreate(BaseModel):
    name: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class ChatChannelUpdate(BaseModel):
    name: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class SendMessageRequest(BaseModel):
    content: str


class AddParticipantRequest(BaseModel):
    user_uuid: str


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
    return [ch.__dict__ for ch in channels]


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
    return channel.__dict__


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
    
    return channel.__dict__


@router.put("/{id}", response_model=dict)
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
    return channel.__dict__


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
    return channel.__dict__


@router.get("/available-participants", response_model=List[dict])
def get_available_participants(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Return users from the same company who can be added as participants
    from app.models.company_user import CompanyUser
    company_users = db.query(CompanyUser).filter(
        CompanyUser.company_uuid == current.company_uuid
    ).all()
    user_uuids = [cu.user_uuid for cu in company_users]
    users = db.query(User).filter(User.uuid.in_(user_uuids)).all()
    return [{"uuid": u.uuid, "name": u.name, "email": u.email} for u in users]


@router.post("/{id}/send-message", response_model=dict)
def send_message(
    id: str,
    payload: SendMessageRequest,
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
    
    # Get or create participant for current user
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.chat_channel_uuid == channel.uuid,
        ChatParticipant.user_uuid == current.uuid,
        ChatParticipant.deleted_at.is_(None)
    ).first()
    
    if not participant:
        participant = ChatParticipant()
        participant.uuid = str(uuid.uuid4())
        participant.company_uuid = current.company_uuid
        participant.chat_channel_uuid = channel.uuid
        participant.user_uuid = current.uuid
        db.add(participant)
        db.commit()
        db.refresh(participant)
    
    # Create message
    message = ChatMessage()
    message.uuid = str(uuid.uuid4())
    message.company_uuid = current.company_uuid
    message.chat_channel_uuid = channel.uuid
    message.sender_uuid = participant.uuid
    message.content = payload.content
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Notify other participants
    from app.models.chat_participant import ChatParticipant
    from app.models.user_device import UserDevice
    from app.utils.push_notifications import push_service
    
    participants = db.query(ChatParticipant).filter(
        ChatParticipant.chat_channel_uuid == channel.uuid,
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
        push_service.send_to_devices(
            registration_ids=device_tokens,
            title=f"New message in {channel.name or 'Chat'}",
            body=payload.content[:100],  # Truncate long messages
            data={
                "type": "chat_message",
                "channel_id": channel.public_id,
                "message_id": message.public_id
            }
        )
    
    return message.__dict__


@router.delete("/delete-message/{chat_message_id}", status_code=status.HTTP_200_OK)
def delete_message(
    chat_message_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    message = db.query(ChatMessage).filter(
        ChatMessage.company_uuid == current.company_uuid,
        (ChatMessage.uuid == chat_message_id) | (ChatMessage.public_id == chat_message_id),
        ChatMessage.deleted_at.is_(None)
    ).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    
    # Check if user is the sender
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


@router.post("/read-message/{chat_message_id}", response_model=dict)
def create_read_receipt(
    chat_message_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    message = db.query(ChatMessage).filter(
        ChatMessage.company_uuid == current.company_uuid,
        (ChatMessage.uuid == chat_message_id) | (ChatMessage.public_id == chat_message_id),
        ChatMessage.deleted_at.is_(None)
    ).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    
    # Get participant for current user
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.chat_channel_uuid == message.chat_channel_uuid,
        ChatParticipant.user_uuid == current.uuid,
        ChatParticipant.deleted_at.is_(None)
    ).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
    
    # Check if receipt already exists
    from app.models.chat_receipt import ChatReceipt
    existing = db.query(ChatReceipt).filter(
        ChatReceipt.chat_message_uuid == message.uuid,
        ChatReceipt.participant_uuid == participant.uuid
    ).first()
    
    if existing:
        return existing.__dict__
    
    # Create receipt
    receipt = ChatReceipt()
    receipt.uuid = str(uuid.uuid4())
    receipt.company_uuid = current.company_uuid
    receipt.chat_message_uuid = message.uuid
    receipt.participant_uuid = participant.uuid
    receipt.read_at = datetime.utcnow()
    
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt.__dict__


@router.post("/{id}/add-participant", response_model=dict)
def add_participant(
    id: str,
    payload: AddParticipantRequest,
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
    
    # Check if participant already exists
    existing = db.query(ChatParticipant).filter(
        ChatParticipant.chat_channel_uuid == channel.uuid,
        ChatParticipant.user_uuid == payload.user_uuid,
        ChatParticipant.deleted_at.is_(None)
    ).first()
    
    if existing:
        return existing.__dict__
    
    participant = ChatParticipant()
    participant.uuid = str(uuid.uuid4())
    participant.company_uuid = current.company_uuid
    participant.chat_channel_uuid = channel.uuid
    participant.user_uuid = payload.user_uuid
    
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant.__dict__


@router.delete("/remove-participant/{participant_id}", status_code=status.HTTP_200_OK)
def remove_participant(
    participant_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.company_uuid == current.company_uuid,
        (ChatParticipant.uuid == participant_id) | (ChatParticipant.public_id == participant_id),
        ChatParticipant.deleted_at.is_(None)
    ).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
    
    participant.deleted_at = datetime.utcnow()
    db.add(participant)
    db.commit()
    return participant.__dict__

