from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from .enums import ThreadStatus


class ChatThread(SQLModel, table=True):
    """A conversation between two users, optionally tied to a listing."""

    __tablename__ = "threads"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    listing_id: Optional[UUID] = Field(default=None, foreign_key="listings.id", index=True)
    starter_id: UUID = Field(foreign_key="users.id", index=True)
    recipient_id: UUID = Field(foreign_key="users.id", index=True)
    status: ThreadStatus = Field(default=ThreadStatus.active, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Message(SQLModel, table=True):
    """A chat message exchanged within a thread."""

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    thread_id: UUID = Field(foreign_key="threads.id", index=True)
    sender_id: UUID = Field(foreign_key="users.id", index=True)
    body: str
    sent_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    read_at: Optional[datetime] = None
