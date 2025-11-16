import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Topic, Subscriber, Subscription, Content, ContentStatus
from app.tasks.newsletter_tasks import get_due_content, get_active_subscribers_for_topic


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_get_due_content(db):
    topic = Topic(name="Technology")
    db.add(topic)
    db.commit()
    
    past_time = datetime.utcnow() - timedelta(hours=1)
    future_time = datetime.utcnow() + timedelta(hours=1)
    
    due_content = Content(
        topic_id=topic.id,
        title="Due Content",
        body="This is due",
        scheduled_at=past_time,
        status=ContentStatus.PENDING
    )
    future_content = Content(
        topic_id=topic.id,
        title="Future Content",
        body="This is not due",
        scheduled_at=future_time,
        status=ContentStatus.PENDING
    )
    sent_content = Content(
        topic_id=topic.id,
        title="Sent Content",
        body="Already sent",
        scheduled_at=past_time,
        status=ContentStatus.SENT
    )
    
    db.add_all([due_content, future_content, sent_content])
    db.commit()
    
    due_list = get_due_content(db)
    assert len(due_list) == 1
    assert due_list[0].id == due_content.id
    assert due_list[0].title == "Due Content"


def test_get_due_content_empty(db):
    due_list = get_due_content(db)
    assert len(due_list) == 0


def test_get_active_subscribers_for_topic(db):
    topic1 = Topic(name="Technology")
    topic2 = Topic(name="Science")
    db.add_all([topic1, topic2])
    db.commit()
    
    subscriber1 = Subscriber(email="user1@example.com", is_active=True)
    subscriber2 = Subscriber(email="user2@example.com", is_active=True)
    subscriber3 = Subscriber(email="user3@example.com", is_active=False)
    db.add_all([subscriber1, subscriber2, subscriber3])
    db.commit()
    
    sub1 = Subscription(subscriber_id=subscriber1.id, topic_id=topic1.id, is_active=True)
    sub2 = Subscription(subscriber_id=subscriber2.id, topic_id=topic1.id, is_active=True)
    sub3 = Subscription(subscriber_id=subscriber3.id, topic_id=topic1.id, is_active=True)
    sub4 = Subscription(subscriber_id=subscriber1.id, topic_id=topic2.id, is_active=True)
    db.add_all([sub1, sub2, sub3, sub4])
    db.commit()
    
    subscribers = get_active_subscribers_for_topic(db, topic1.id)
    assert len(subscribers) == 2
    assert subscriber1 in subscribers
    assert subscriber2 in subscribers
    assert subscriber3 not in subscribers


def test_get_active_subscribers_inactive_subscription(db):
    topic = Topic(name="Technology")
    db.add(topic)
    db.commit()
    
    subscriber = Subscriber(email="user1@example.com", is_active=True)
    db.add(subscriber)
    db.commit()
    
    subscription = Subscription(
        subscriber_id=subscriber.id,
        topic_id=topic.id,
        is_active=False
    )
    db.add(subscription)
    db.commit()
    
    subscribers = get_active_subscribers_for_topic(db, topic.id)
    assert len(subscribers) == 0


def test_get_active_subscribers_inactive_subscriber(db):
    topic = Topic(name="Technology")
    db.add(topic)
    db.commit()
    
    subscriber = Subscriber(email="user1@example.com", is_active=False)
    db.add(subscriber)
    db.commit()
    
    subscription = Subscription(
        subscriber_id=subscriber.id,
        topic_id=topic.id,
        is_active=True
    )
    db.add(subscription)
    db.commit()
    
    subscribers = get_active_subscribers_for_topic(db, topic.id)
    assert len(subscribers) == 0

