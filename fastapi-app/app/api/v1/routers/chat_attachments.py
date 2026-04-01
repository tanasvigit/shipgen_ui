from typing import List, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.chat_attachment import ChatAttachment
from app.models.user import User

router = APIRouter(prefix="/int/v1/chat-attachments", tags=["chat-attachments"])


class ChatAttachmentCreate(BaseModel):
    chat_channel_uuid: str
    chat_message_uuid: Optional[str] = None
    file_uuid: str


@router.get("/", response_model=List[dict])
def list_chat_attachments(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    chat_channel_uuid: Optional[str] = Query(None),
    chat_message_uuid: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(ChatAttachment).filter(
        ChatAttachment.company_uuid == current.company_uuid,
        ChatAttachment.deleted_at.is_(None)
    )
    
    if chat_channel_uuid:
        query = query.filter(ChatAttachment.chat_channel_uuid == chat_channel_uuid)
    if chat_message_uuid:
        query = query.filter(ChatAttachment.chat_message_uuid == chat_message_uuid)
    
    attachments = query.offset(offset).limit(limit).all()
    return [a.__dict__ for a in attachments]


@router.get("/{id}", response_model=dict)
def get_chat_attachment(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    attachment = db.query(ChatAttachment).filter(
        ChatAttachment.company_uuid == current.company_uuid,
        (ChatAttachment.uuid == id) | (ChatAttachment.public_id == id),
        ChatAttachment.deleted_at.is_(None)
    ).first()
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat attachment not found")
    return attachment.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_chat_attachment(
    payload: ChatAttachmentCreate,
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
    
    attachment = ChatAttachment()
    attachment.uuid = str(uuid.uuid4())
    attachment.company_uuid = current.company_uuid
    attachment.chat_channel_uuid = payload.chat_channel_uuid
    attachment.chat_message_uuid = payload.chat_message_uuid
    attachment.sender_uuid = participant.uuid
    attachment.file_uuid = payload.file_uuid
    
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_chat_attachment(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    attachment = db.query(ChatAttachment).filter(
        ChatAttachment.company_uuid == current.company_uuid,
        (ChatAttachment.uuid == id) | (ChatAttachment.public_id == id),
        ChatAttachment.deleted_at.is_(None)
    ).first()
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat attachment not found")
    
    # Check if user is the sender
    from app.models.chat_participant import ChatParticipant
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.uuid == attachment.sender_uuid,
        ChatParticipant.user_uuid == current.uuid
    ).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this attachment")
    
    attachment.deleted_at = datetime.utcnow()
    db.add(attachment)
    db.commit()
    return attachment.__dict__

