import logging
from datetime import datetime
from typing import List
from celery import Task
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Content, Subscription, Subscriber, ContentStatus
from celery_worker import celery

logger = logging.getLogger(__name__)


def get_due_content(db: Session) -> List[Content]:
    """Query database for content that is due to be sent."""
    now = datetime.utcnow()
    due_content = (
        db.query(Content)
        .filter(
            Content.status == ContentStatus.PENDING.value,
            Content.scheduled_at <= now
        )
        .all()
    )
    return due_content


def get_active_subscribers_for_topic(db: Session, topic_id: int) -> List[Subscriber]:
    """Get all active subscribers for a given topic."""
    subscribers = (
        db.query(Subscriber)
        .join(Subscription)
        .filter(
            Subscription.topic_id == topic_id,
            Subscription.is_active == True,
            Subscriber.is_active == True
        )
        .all()
    )
    return subscribers


@celery.task(bind=True, name="app.tasks.check_due_content")
def check_due_content(self: Task):
    """Periodic task to check for due content and enqueue send tasks."""
    db = SessionLocal()
    try:
        due_content_list = get_due_content(db)
        logger.info(f"Found {len(due_content_list)} content items due for sending")
        
        for content in due_content_list:
            send_content_to_subscribers.delay(content.id)
            logger.info(f"Enqueued send task for content ID: {content.id}")
        
        return {"checked": len(due_content_list), "enqueued": len(due_content_list)}
    except Exception as e:
        logger.error(f"Error in check_due_content: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


@celery.task(bind=True, name="app.tasks.send_content_to_subscribers", max_retries=3)
def send_content_to_subscribers(self: Task, content_id: int):
    """Send content to all active subscribers of the content's topic."""
    db = SessionLocal()
    try:
        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            logger.error(f"Content with ID {content_id} not found")
            return {"status": "error", "message": "Content not found"}
        
        if content.status != ContentStatus.PENDING:
            logger.warning(f"Content {content_id} is not in PENDING status (current: {content.status})")
            return {"status": "skipped", "message": f"Content status is {content.status}"}
        
        subscribers = get_active_subscribers_for_topic(db, content.topic_id)
        logger.info(f"Found {len(subscribers)} active subscribers for topic {content.topic_id}")
        
        if not subscribers:
            logger.warning(f"No active subscribers found for topic {content.topic_id}")
            content.status = ContentStatus.SENT
            content.sent_at = datetime.utcnow()
            db.commit()
            return {"status": "completed", "sent": 0, "message": "No subscribers"}
        
        from app.services.email_service import send_email
        
        success_count = 0
        error_messages = []
        
        for subscriber in subscribers:
            try:
                send_email(
                    to_email=subscriber.email,
                    subject=content.title or f"Newsletter: {content.topic.name}",
                    body=content.body
                )
                success_count += 1
                logger.info(f"Sent email to {subscriber.email} for content {content_id}")
            except Exception as e:
                error_msg = f"Failed to send to {subscriber.email}: {str(e)}"
                error_messages.append(error_msg)
                logger.error(error_msg, exc_info=True)
        
        if success_count > 0:
            content.status = ContentStatus.SENT
            content.sent_at = datetime.utcnow()
            if error_messages:
                content.error_message = "; ".join(error_messages[:5])  # Store first 5 errors
        else:
            content.status = ContentStatus.FAILED
            content.error_message = "; ".join(error_messages[:5])
        
        db.commit()
        db.refresh(content)
        
        return {
            "status": "completed",
            "content_id": content_id,
            "sent": success_count,
            "failed": len(error_messages),
            "total_subscribers": len(subscribers)
        }
        
    except Exception as e:
        logger.error(f"Error in send_content_to_subscribers for content {content_id}: {str(e)}", exc_info=True)
        
        # Update content status to failed
        try:
            content = db.query(Content).filter(Content.id == content_id).first()
            if content:
                content.status = ContentStatus.FAILED
                content.error_message = str(e)
                db.commit()
        except Exception as db_error:
            logger.error(f"Error updating content status: {str(db_error)}")
        
        # Retry the task
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()

