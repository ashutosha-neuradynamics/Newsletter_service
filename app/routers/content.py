from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import Content, Topic, ContentStatus
from app.schemas import ContentCreate, ContentUpdate, ContentResponse

router = APIRouter(prefix="/api/content", tags=["content"])


@router.post("/", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
def create_content(content: ContentCreate, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == content.topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    db_content = Content(**content.model_dump())
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content


@router.get("/", response_model=List[ContentResponse])
def list_content(
    skip: int = 0,
    limit: int = 100,
    topic_id: Optional[int] = Query(None),
    status: Optional[ContentStatus] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Content)
    
    if topic_id is not None:
        query = query.filter(Content.topic_id == topic_id)
    if status is not None:
        query = query.filter(Content.status == status.value)
    
    content_list = query.order_by(Content.scheduled_at).offset(skip).limit(limit).all()
    return content_list


@router.get("/{content_id}", response_model=ContentResponse)
def get_content(content_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    return content


@router.patch("/{content_id}", response_model=ContentResponse)
def update_content(content_id: int, content_update: ContentUpdate, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    update_data = content_update.model_dump(exclude_unset=True)
    
    if "topic_id" in update_data:
        topic = db.query(Topic).filter(Topic.id == update_data["topic_id"]).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )
    
    for field, value in update_data.items():
        setattr(content, field, value)
    
    db.commit()
    db.refresh(content)
    return content


