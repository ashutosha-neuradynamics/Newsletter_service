from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Topic
from app.schemas import TopicCreate, TopicUpdate, TopicResponse

router = APIRouter(prefix="/api/topics", tags=["topics"])


@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
def create_topic(topic: TopicCreate, db: Session = Depends(get_db)):
    db_topic = db.query(Topic).filter(Topic.name == topic.name).first()
    if db_topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic with this name already exists"
        )
    db_topic = Topic(**topic.model_dump())
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic


@router.get("/", response_model=List[TopicResponse])
def list_topics(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    topics = db.query(Topic).offset(skip).limit(limit).all()
    return topics


@router.get("/{topic_id}", response_model=TopicResponse)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    return topic


@router.patch("/{topic_id}", response_model=TopicResponse)
def update_topic(topic_id: int, topic_update: TopicUpdate, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    update_data = topic_update.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing_topic = db.query(Topic).filter(
            Topic.name == update_data["name"],
            Topic.id != topic_id
        ).first()
        if existing_topic:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Topic with this name already exists"
            )
    
    for field, value in update_data.items():
        setattr(topic, field, value)
    
    db.commit()
    db.refresh(topic)
    return topic


@router.delete("/{topic_id}", status_code=status.HTTP_200_OK)
def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    db.delete(topic)
    db.commit()
    return {"message": "Topic deleted successfully"}


