from typing import List, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.chat_receipt import ChatReceipt
from app.models.user import User

router = APIRouter(prefix="/int/v1/chat-receipts", tags=["chat-receipts"])


class ChatReceiptCreate(BaseModel):
    chat_message_uuid: str


@router.get("/", response_model=List[dict])
def list_chat_receipts(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    chat_message_uuid: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(ChatReceipt).filter(
        ChatReceipt.company_uuid == current.company_uuid
    )
    
    if chat_message_uuid:
        query = query.filter(ChatReceipt.chat_message_uuid == chat_message_uuid)
    
    receipts = query.offset(offset).limit(limit).all()
    return [r.__dict__ for r in receipts]


@router.get("/{id}", response_model=dict)
def get_chat_receipt(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    receipt = db.query(ChatReceipt).filter(
        ChatReceipt.company_uuid == current.company_uuid,
        (ChatReceipt.uuid == id) | (ChatReceipt.public_id == id)
    ).first()
    if not receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat receipt not found")
    return receipt.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_chat_receipt(
    payload: ChatReceiptCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Get message
    from app.models.chat_message import ChatMessage
    message = db.query(ChatMessage).filter(
        ChatMessage.company_uuid == current.company_uuid,
        (ChatMessage.uuid == payload.chat_message_uuid) | (ChatMessage.public_id == payload.chat_message_uuid),
        ChatMessage.deleted_at.is_(None)
    ).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat message not found")
    
    # Get participant for current user
    from app.models.chat_participant import ChatParticipant
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.chat_channel_uuid == message.chat_channel_uuid,
        ChatParticipant.user_uuid == current.uuid,
        ChatParticipant.deleted_at.is_(None)
    ).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
    
    # Check if receipt already exists
    existing = db.query(ChatReceipt).filter(
        ChatReceipt.chat_message_uuid == message.uuid,
        ChatReceipt.participant_uuid == participant.uuid
    ).first()
    
    if existing:
        return existing.__dict__
    
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


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_chat_receipt(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    receipt = db.query(ChatReceipt).filter(
        ChatReceipt.company_uuid == current.company_uuid,
        (ChatReceipt.uuid == id) | (ChatReceipt.public_id == id)
    ).first()
    if not receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat receipt not found")
    
    db.delete(receipt)
    db.commit()
    return {"message": "Chat receipt deleted"}

