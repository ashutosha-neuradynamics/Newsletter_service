from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.models import ContentStatus


class TopicBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class TopicCreate(TopicBase):
    pass


class TopicUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TopicResponse(TopicBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriberBase(BaseModel):
    email: EmailStr


class SubscriberCreate(SubscriberBase):
    pass


class SubscriberUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class SubscriberResponse(SubscriberBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionCreate(BaseModel):
    subscriber_id: int
    topic_id: int


class SubscriptionUpdate(BaseModel):
    is_active: Optional[bool] = None


class SubscriptionResponse(BaseModel):
    id: int
    subscriber_id: int
    topic_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ContentBase(BaseModel):
    topic_id: int
    title: Optional[str] = Field(None, max_length=255)
    body: str = Field(..., min_length=1)
    scheduled_at: datetime


class ContentCreate(ContentBase):
    pass


class ContentUpdate(BaseModel):
    topic_id: Optional[int] = None
    title: Optional[str] = Field(None, max_length=255)
    body: Optional[str] = Field(None, min_length=1)
    scheduled_at: Optional[datetime] = None
    status: Optional[ContentStatus] = None


class ContentResponse(ContentBase):
    id: int
    status: ContentStatus
    created_at: datetime
    updated_at: datetime
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


