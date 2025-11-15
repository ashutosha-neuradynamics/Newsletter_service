from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Subscription, Subscriber, Topic
from app.schemas import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


@router.post(
    "/", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED
)
def create_subscription(
    subscription: SubscriptionCreate, db: Session = Depends(get_db)
):
    subscriber = (
        db.query(Subscriber).filter(Subscriber.id == subscription.subscriber_id).first()
    )
    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subscriber not found"
        )

    topic = db.query(Topic).filter(Topic.id == subscription.topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found"
        )

    existing_subscription = (
        db.query(Subscription)
        .filter(
            Subscription.subscriber_id == subscription.subscriber_id,
            Subscription.topic_id == subscription.topic_id,
        )
        .first()
    )
    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscription already exists",
        )

    db_subscription = Subscription(**subscription.model_dump())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


@router.get("/", response_model=List[SubscriptionResponse])
def list_subscriptions(
    skip: int = 0,
    limit: int = 100,
    subscriber_id: Optional[int] = Query(None),
    topic_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Subscription)

    if subscriber_id is not None:
        query = query.filter(Subscription.subscriber_id == subscriber_id)
    if topic_id is not None:
        query = query.filter(Subscription.topic_id == topic_id)

    subscriptions = query.offset(skip).limit(limit).all()
    return subscriptions


@router.patch("/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(
    subscription_id: int,
    subscription_update: SubscriptionUpdate,
    db: Session = Depends(get_db),
):
    subscription = (
        db.query(Subscription).filter(Subscription.id == subscription_id).first()
    )
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found"
        )

    update_data = subscription_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subscription, field, value)

    db.commit()
    db.refresh(subscription)
    return subscription
