import pytest
from datetime import datetime, timedelta
from app.models import Topic, Subscriber, Subscription, Content, ContentStatus
from app.database import SessionLocal, engine, Base


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_create_topic(db):
    topic = Topic(name="Technology", description="Tech news and updates")
    db.add(topic)
    db.commit()
    db.refresh(topic)

    assert topic.id is not None
    assert topic.name == "Technology"
    assert topic.description == "Tech news and updates"
    assert topic.is_active is True
    assert topic.created_at is not None


def test_create_subscriber(db):
    subscriber = Subscriber(email="test@example.com")
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)

    assert subscriber.id is not None
    assert subscriber.email == "test@example.com"
    assert subscriber.is_active is True
    assert subscriber.created_at is not None


def test_create_subscription(db):
    topic = Topic(name="Technology")
    subscriber = Subscriber(email="test@example.com")
    db.add(topic)
    db.add(subscriber)
    db.commit()

    subscription = Subscription(subscriber_id=subscriber.id, topic_id=topic.id)
    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    assert subscription.id is not None
    assert subscription.subscriber_id == subscriber.id
    assert subscription.topic_id == topic.id
    assert subscription.is_active is True
    assert subscription.created_at is not None


def test_subscriber_can_subscribe_to_multiple_topics(db):
    subscriber = Subscriber(email="test@example.com")
    topic1 = Topic(name="Technology")
    topic2 = Topic(name="Science")
    db.add_all([subscriber, topic1, topic2])
    db.commit()

    sub1 = Subscription(subscriber_id=subscriber.id, topic_id=topic1.id)
    sub2 = Subscription(subscriber_id=subscriber.id, topic_id=topic2.id)
    db.add_all([sub1, sub2])
    db.commit()

    db.refresh(subscriber)
    assert len(subscriber.subscriptions) == 2


def test_create_content(db):
    topic = Topic(name="Technology")
    db.add(topic)
    db.commit()

    scheduled_at = datetime.utcnow() + timedelta(hours=1)
    content = Content(
        topic_id=topic.id,
        title="Weekly Tech Update",
        body="This is the content body",
        scheduled_at=scheduled_at
    )
    db.add(content)
    db.commit()
    db.refresh(content)

    assert content.id is not None
    assert content.topic_id == topic.id
    assert content.title == "Weekly Tech Update"
    assert content.body == "This is the content body"
    assert content.scheduled_at == scheduled_at
    assert content.status == ContentStatus.PENDING
    assert content.created_at is not None
    assert content.updated_at is not None


def test_content_relationships(db):
    topic = Topic(name="Technology")
    subscriber1 = Subscriber(email="user1@example.com")
    subscriber2 = Subscriber(email="user2@example.com")
    db.add_all([topic, subscriber1, subscriber2])
    db.commit()

    sub1 = Subscription(subscriber_id=subscriber1.id, topic_id=topic.id)
    sub2 = Subscription(subscriber_id=subscriber2.id, topic_id=topic.id)
    db.add_all([sub1, sub2])
    db.commit()

    content = Content(
        topic_id=topic.id,
        title="Test Content",
        body="Body",
        scheduled_at=datetime.utcnow() + timedelta(hours=1)
    )
    db.add(content)
    db.commit()

    db.refresh(topic)
    assert len(topic.content) == 1
    assert topic.content[0].id == content.id

    db.refresh(topic)
    assert len(topic.subscriptions) == 2


def test_topic_unique_name_constraint(db):
    topic1 = Topic(name="Technology")
    db.add(topic1)
    db.commit()

    topic2 = Topic(name="Technology")
    db.add(topic2)
    with pytest.raises(Exception):
        db.commit()


def test_subscriber_unique_email_constraint(db):
    subscriber1 = Subscriber(email="test@example.com")
    db.add(subscriber1)
    db.commit()

    subscriber2 = Subscriber(email="test@example.com")
    db.add(subscriber2)
    with pytest.raises(Exception):
        db.commit()

