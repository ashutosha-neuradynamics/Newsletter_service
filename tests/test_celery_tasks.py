import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Topic, Subscriber, Subscription, Content, ContentStatus
from app.tasks.newsletter_tasks import check_due_content, send_content_to_subscribers
from celery_worker import celery


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def setup_celery_eager():
    """Run Celery tasks synchronously for testing."""
    celery.conf.task_always_eager = True
    celery.conf.task_eager_propagates = True
    yield
    celery.conf.task_always_eager = False
    celery.conf.task_eager_propagates = False


def test_check_due_content_enqueues_tasks(db):
    topic = Topic(name="Technology")
    db.add(topic)
    db.commit()
    
    past_time = datetime.utcnow() - timedelta(minutes=5)
    content1 = Content(
        topic_id=topic.id,
        title="Content 1",
        body="Body 1",
        scheduled_at=past_time,
        status=ContentStatus.PENDING
    )
    content2 = Content(
        topic_id=topic.id,
        title="Content 2",
        body="Body 2",
        scheduled_at=past_time,
        status=ContentStatus.PENDING
    )
    db.add_all([content1, content2])
    db.commit()
    
    with patch("app.tasks.newsletter_tasks.send_content_to_subscribers.delay") as mock_delay:
        result = check_due_content()
        
        assert result["checked"] == 2
        assert result["enqueued"] == 2
        assert mock_delay.call_count == 2


@patch("app.services.email_service.send_email")
def test_send_content_to_subscribers_success(mock_send_email, db):
    mock_send_email.return_value = True
    
    topic = Topic(name="Technology")
    subscriber1 = Subscriber(email="user1@example.com", is_active=True)
    subscriber2 = Subscriber(email="user2@example.com", is_active=True)
    db.add_all([topic, subscriber1, subscriber2])
    db.commit()
    
    sub1 = Subscription(subscriber_id=subscriber1.id, topic_id=topic.id, is_active=True)
    sub2 = Subscription(subscriber_id=subscriber2.id, topic_id=topic.id, is_active=True)
    db.add_all([sub1, sub2])
    db.commit()
    
    past_time = datetime.utcnow() - timedelta(minutes=5)
    content = Content(
        topic_id=topic.id,
        title="Test Newsletter",
        body="Test body",
        scheduled_at=past_time,
        status=ContentStatus.PENDING
    )
    db.add(content)
    db.commit()
    
    result = send_content_to_subscribers(content.id)
    
    assert result["status"] == "completed"
    assert result["sent"] == 2
    assert result["failed"] == 0
    assert result["total_subscribers"] == 2
    
    db.refresh(content)
    assert content.status == ContentStatus.SENT
    assert content.sent_at is not None
    assert mock_send_email.call_count == 2


@patch("app.services.email_service.send_email")
def test_send_content_to_subscribers_no_subscribers(mock_send_email, db):
    topic = Topic(name="Technology")
    db.add(topic)
    db.commit()
    
    past_time = datetime.utcnow() - timedelta(minutes=5)
    content = Content(
        topic_id=topic.id,
        title="Test Newsletter",
        body="Test body",
        scheduled_at=past_time,
        status=ContentStatus.PENDING
    )
    db.add(content)
    db.commit()
    
    result = send_content_to_subscribers(content.id)
    
    assert result["status"] == "completed"
    assert result["sent"] == 0
    assert result["message"] == "No subscribers"
    
    db.refresh(content)
    assert content.status == ContentStatus.SENT
    assert mock_send_email.call_count == 0


@patch("app.services.email_service.send_email")
def test_send_content_to_subscribers_partial_failure(mock_send_email, db):
    def side_effect(to_email, subject, body, from_email=None):
        if to_email == "user1@example.com":
            raise Exception("SMTP error")
        return True
    
    mock_send_email.side_effect = side_effect
    
    topic = Topic(name="Technology")
    subscriber1 = Subscriber(email="user1@example.com", is_active=True)
    subscriber2 = Subscriber(email="user2@example.com", is_active=True)
    db.add_all([topic, subscriber1, subscriber2])
    db.commit()
    
    sub1 = Subscription(subscriber_id=subscriber1.id, topic_id=topic.id, is_active=True)
    sub2 = Subscription(subscriber_id=subscriber2.id, topic_id=topic.id, is_active=True)
    db.add_all([sub1, sub2])
    db.commit()
    
    past_time = datetime.utcnow() - timedelta(minutes=5)
    content = Content(
        topic_id=topic.id,
        title="Test Newsletter",
        body="Test body",
        scheduled_at=past_time,
        status=ContentStatus.PENDING
    )
    db.add(content)
    db.commit()
    
    result = send_content_to_subscribers(content.id)
    
    assert result["status"] == "completed"
    assert result["sent"] == 1
    assert result["failed"] == 1
    
    db.refresh(content)
    assert content.status == ContentStatus.SENT
    assert content.error_message is not None


@patch("app.services.email_service.send_email")
def test_send_content_to_subscribers_all_fail(mock_send_email, db):
    mock_send_email.side_effect = Exception("SMTP error")
    
    topic = Topic(name="Technology")
    subscriber = Subscriber(email="user1@example.com", is_active=True)
    db.add_all([topic, subscriber])
    db.commit()
    
    sub = Subscription(subscriber_id=subscriber.id, topic_id=topic.id, is_active=True)
    db.add(sub)
    db.commit()
    
    past_time = datetime.utcnow() - timedelta(minutes=5)
    content = Content(
        topic_id=topic.id,
        title="Test Newsletter",
        body="Test body",
        scheduled_at=past_time,
        status=ContentStatus.PENDING
    )
    db.add(content)
    db.commit()
    
    result = send_content_to_subscribers(content.id)
    
    assert result["status"] == "completed"
    assert result["sent"] == 0
    assert result["failed"] == 1
    
    db.refresh(content)
    assert content.status == ContentStatus.FAILED
    assert content.error_message is not None


def test_send_content_to_subscribers_not_found(db):
    result = send_content_to_subscribers(99999)
    assert result["status"] == "error"
    assert "not found" in result["message"].lower()


def test_send_content_to_subscribers_already_sent(db):
    topic = Topic(name="Technology")
    db.add(topic)
    db.commit()
    
    past_time = datetime.utcnow() - timedelta(minutes=5)
    content = Content(
        topic_id=topic.id,
        title="Test Newsletter",
        body="Test body",
        scheduled_at=past_time,
        status=ContentStatus.SENT
    )
    db.add(content)
    db.commit()
    
    result = send_content_to_subscribers(content.id)
    assert result["status"] == "skipped"

