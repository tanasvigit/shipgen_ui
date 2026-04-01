from typing import List, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.chat_participant import ChatParticipant
from app.models.user import User

router = APIRouter(prefix="/int/v1/chat-participants", tags=["chat-participants"])


class ChatParticipantCreate(BaseModel):
    chat_channel_uuid: str
    user_uuid: str


@router.get("/", response_model=List[dict])
def list_chat_participants(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    chat_channel_uuid: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(ChatParticipant).filter(
        ChatParticipant.company_uuid == current.company_uuid,
        ChatParticipant.deleted_at.is_(None)
    )
    
    if chat_channel_uuid:
        query = query.filter(ChatParticipant.chat_channel_uuid == chat_channel_uuid)
    
    participants = query.offset(offset).limit(limit).all()
    return [p.__dict__ for p in participants]


@router.get("/{id}", response_model=dict)
def get_chat_participant(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.company_uuid == current.company_uuid,
        (ChatParticipant.uuid == id) | (ChatParticipant.public_id == id),
        ChatParticipant.deleted_at.is_(None)
    ).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat participant not found")
    return participant.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_chat_participant(
    payload: ChatParticipantCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Check if participant already exists
    existing = db.query(ChatParticipant).filter(
        ChatParticipant.chat_channel_uuid == payload.chat_channel_uuid,
        ChatParticipant.user_uuid == payload.user_uuid,
        ChatParticipant.deleted_at.is_(None)
    ).first()
    
    if existing:
        return existing.__dict__
    
    participant = ChatParticipant()
    participant.uuid = str(uuid.uuid4())
    participant.company_uuid = current.company_uuid
    participant.chat_channel_uuid = payload.chat_channel_uuid
    participant.user_uuid = payload.user_uuid
    
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_chat_participant(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.company_uuid == current.company_uuid,
        (ChatParticipant.uuid == id) | (ChatParticipant.public_id == id),
        ChatParticipant.deleted_at.is_(None)
    ).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat participant not found")
    
    participant.deleted_at = datetime.utcnow()
    db.add(participant)
    db.commit()
    return participant.__dict__

