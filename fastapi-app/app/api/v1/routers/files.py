from typing import List, Optional, Any
import uuid
import base64
from datetime import datetime, timezone
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File as FastAPIFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.file import File
from app.models.user import User
from app.utils.file_storage import file_storage

router = APIRouter(prefix="/v1/files", tags=["files"])


class FileCreate(BaseModel):
    subject_uuid: Optional[str] = None
    subject_type: Optional[str] = None
    disk: Optional[str] = None
    path: Optional[str] = None
    bucket: Optional[str] = None
    folder: Optional[str] = None
    type: Optional[str] = None
    caption: Optional[str] = None


class FileUpdate(BaseModel):
    subject_uuid: Optional[str] = None
    subject_type: Optional[str] = None
    caption: Optional[str] = None


class Base64FileCreate(BaseModel):
    file: str  # base64 encoded file
    filename: Optional[str] = None
    path: str = "uploads"
    type: str = "image"
    content_type: Optional[str] = None


@router.get("/", response_model=List[dict])
def list_files(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    files = db.query(File).filter(
        File.company_uuid == current.company_uuid,
        File.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [f.__dict__ for f in files]


@router.get("/{id}", response_model=dict)
def get_file(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    file = db.query(File).filter(
        File.company_uuid == current.company_uuid,
        (File.uuid == id) | (File.public_id == id),
        File.deleted_at.is_(None)
    ).first()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return file.__dict__


@router.get("/{id}/download")
def download_file(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    file = db.query(File).filter(
        File.company_uuid == current.company_uuid,
        (File.uuid == id) | (File.public_id == id),
        File.deleted_at.is_(None)
    ).first()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    if not file.path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File path not found")
    
    try:
        file_content = file_storage.get_file(file.path, file.disk)
        filename = file.original_filename or f"file_{file.uuid}"
        content_type = file.content_type or "application/octet-stream"
        
        return StreamingResponse(
            BytesIO(file_content),
            media_type=content_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found in storage")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error downloading file: {str(e)}")


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_file(
    payload: FileCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    file = File()
    file.uuid = str(uuid.uuid4())
    file.company_uuid = current.company_uuid
    file.uploader_uuid = current.uuid
    file.subject_uuid = payload.subject_uuid
    file.subject_type = payload.subject_type
    file.disk = payload.disk
    file.path = payload.path
    file.bucket = payload.bucket
    file.folder = payload.folder
    file.type = payload.type
    file.caption = payload.caption
    
    db.add(file)
    db.commit()
    db.refresh(file)
    return file.__dict__


@router.post("/base64", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_file_from_base64(
    payload: Base64FileCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    try:
        # Decode base64 file
        if payload.file.startswith("data:"):
            # Remove data URL prefix if present
            header, encoded = payload.file.split(",", 1)
            file_content = base64.b64decode(encoded)
        else:
            file_content = base64.b64decode(payload.file)
        
        filename = payload.filename or f"{uuid.uuid4()}.png"
        folder = payload.path or "uploads"
        
        # Save file to storage
        storage_path, disk_type = file_storage.save_file(
            file_content,
            filename,
            folder=folder,
            content_type=payload.content_type or "image/png"
        )
        
        # Create file record
        file = File()
        file.uuid = str(uuid.uuid4())
        file.public_id = f"file_{uuid.uuid4().hex[:12]}"
        file.company_uuid = current.company_uuid
        file.uploader_uuid = current.uuid
        file.path = storage_path
        file.disk = disk_type
        file.type = payload.type
        file.content_type = payload.content_type or "image/png"
        file.original_filename = filename
        file.file_size = len(file_content)
        file.created_at = datetime.now(timezone.utc)
        file.updated_at = datetime.now(timezone.utc)
        
        db.add(file)
        db.commit()
        db.refresh(file)
        return file.__dict__
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error uploading file: {str(e)}")


@router.put("/{id}", response_model=dict)
def update_file(
    id: str,
    payload: FileUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    file = db.query(File).filter(
        File.company_uuid == current.company_uuid,
        (File.uuid == id) | (File.public_id == id),
        File.deleted_at.is_(None)
    ).first()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(file, field):
            setattr(file, field, value)
    
    db.add(file)
    db.commit()
    db.refresh(file)
    return file.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_file(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    file = db.query(File).filter(
        File.company_uuid == current.company_uuid,
        (File.uuid == id) | (File.public_id == id),
        File.deleted_at.is_(None)
    ).first()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    file.deleted_at = datetime.utcnow()
    db.add(file)
    db.commit()
    return file.__dict__

