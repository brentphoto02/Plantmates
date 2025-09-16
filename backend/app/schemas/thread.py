from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel

from ..models.enums import ThreadStatus


class ThreadBase(SQLModel):
    """Shared thread fields."""

    listing_id: Optional[UUID] = None
    starter_id: UUID
    recipient_id: UUID
    status: ThreadStatus = Field(default=ThreadStatus.active)


class ThreadCreate(SQLModel):
    """Payload for creating or retrieving a thread."""

    listing_id: Optional[UUID] = None
    starter_id: UUID
    recipient_id: UUID


class ThreadRead(ThreadBase):
    """Thread representation returned by the API."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class MessageCreate(SQLModel):
    """Payload for creating a new message."""

    thread_id: UUID
    sender_id: UUID
    body: str = Field(min_length=1, max_length=2000)


class MessageRead(SQLModel):
    """Message representation returned by the API."""

    id: UUID
    thread_id: UUID
    sender_id: UUID
    body: str
    sent_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ThreadWithMessages(ThreadRead):
    """Thread plus its most recent messages."""

    messages: list[MessageRead] = Field(default_factory=list)
