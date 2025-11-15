from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Subscriber
from app.schemas import SubscriberCreate, SubscriberUpdate, SubscriberResponse

router = APIRouter(prefix="/api/subscribers", tags=["subscribers"])


@router.post("/", response_model=SubscriberResponse, status_code=status.HTTP_201_CREATED)
def create_subscriber(subscriber: SubscriberCreate, db: Session = Depends(get_db)):
    db_subscriber = db.query(Subscriber).filter(Subscriber.email == subscriber.email).first()
    if db_subscriber:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscriber with this email already exists"
        )
    db_subscriber = Subscriber(**subscriber.model_dump())
    db.add(db_subscriber)
    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber


@router.get("/", response_model=List[SubscriberResponse])
def list_subscribers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subscribers = db.query(Subscriber).offset(skip).limit(limit).all()
    return subscribers


@router.get("/{subscriber_id}", response_model=SubscriberResponse)
def get_subscriber(subscriber_id: int, db: Session = Depends(get_db)):
    subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()
    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscriber not found"
        )
    return subscriber


@router.patch("/{subscriber_id}", response_model=SubscriberResponse)
def update_subscriber(subscriber_id: int, subscriber_update: SubscriberUpdate, db: Session = Depends(get_db)):
    subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()
    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscriber not found"
        )
    
    update_data = subscriber_update.model_dump(exclude_unset=True)
    if "email" in update_data:
        existing_subscriber = db.query(Subscriber).filter(
            Subscriber.email == update_data["email"],
            Subscriber.id != subscriber_id
        ).first()
        if existing_subscriber:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscriber with this email already exists"
            )
    
    for field, value in update_data.items():
        setattr(subscriber, field, value)
    
    db.commit()
    db.refresh(subscriber)
    return subscriber


