from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_
from sqlmodel import Session, select

from ..db.session import get_session
from ..models import ChatThread, Message
from ..schemas import (
    MessageCreate,
    MessageRead,
    ThreadCreate,
    ThreadRead,
    ThreadWithMessages,
)

router = APIRouter(prefix="/threads", tags=["threads"])


def _thread_to_read(session: Session, thread: ChatThread) -> ThreadRead:
    thread_read = ThreadRead.from_orm(thread)
    last_message = session.exec(
        select(Message)
        .where(Message.thread_id == thread.id)
        .order_by(Message.sent_at.desc())
        .limit(1)
    ).first()
    if last_message:
        thread_read.last_message_at = last_message.sent_at
    return thread_read


@router.post("/", response_model=ThreadRead, status_code=status.HTTP_201_CREATED)
def create_thread(thread_in: ThreadCreate, session: Session = Depends(get_session)) -> ThreadRead:
    """Create a thread for two participants, or return the existing conversation."""

    listing_filter = (
        ChatThread.listing_id == thread_in.listing_id
        if thread_in.listing_id is not None
        else ChatThread.listing_id.is_(None)
    )
    statement = select(ChatThread).where(
        listing_filter,
        or_(
            and_(
                ChatThread.starter_id == thread_in.starter_id,
                ChatThread.recipient_id == thread_in.recipient_id,
            ),
            and_(
                ChatThread.starter_id == thread_in.recipient_id,
                ChatThread.recipient_id == thread_in.starter_id,
            ),
        ),
    )
    existing = session.exec(statement).first()
    if existing:
        return _thread_to_read(session, existing)

    now = datetime.utcnow()
    thread = ChatThread(
        listing_id=thread_in.listing_id,
        starter_id=thread_in.starter_id,
        recipient_id=thread_in.recipient_id,
        created_at=now,
        updated_at=now,
    )
    session.add(thread)
    session.commit()
    session.refresh(thread)
    return _thread_to_read(session, thread)


@router.get("/", response_model=list[ThreadRead])
def list_threads(
    *,
    session: Session = Depends(get_session),
    user_id: UUID = Query(...),
    listing_id: Optional[UUID] = Query(default=None),
) -> list[ThreadRead]:
    """List threads for a user, optionally filtered by listing."""

    statement = select(ChatThread).where(
        or_(ChatThread.starter_id == user_id, ChatThread.recipient_id == user_id)
    )
    if listing_id:
        statement = statement.where(ChatThread.listing_id == listing_id)

    threads = session.exec(statement).all()
    threads.sort(key=lambda thread: thread.updated_at, reverse=True)
    return [_thread_to_read(session, thread) for thread in threads]


@router.get("/{thread_id}", response_model=ThreadWithMessages)
def get_thread(thread_id: UUID, session: Session = Depends(get_session)) -> ThreadWithMessages:
    """Return a thread along with its messages."""

    thread = session.get(ChatThread, thread_id)
    if not thread:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")

    thread_read = _thread_to_read(session, thread)
    messages = session.exec(
        select(Message).where(Message.thread_id == thread_id).order_by(Message.sent_at)
    ).all()
    message_reads = [MessageRead.from_orm(message) for message in messages]
    return ThreadWithMessages(**thread_read.dict(), messages=message_reads)


@router.post("/{thread_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def create_message(
    thread_id: UUID,
    message_in: MessageCreate,
    session: Session = Depends(get_session),
) -> MessageRead:
    """Create a new message within a thread."""

    thread = session.get(ChatThread, thread_id)
    if not thread:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")

    if message_in.sender_id not in {thread.starter_id, thread.recipient_id}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sender not part of thread")

    now = datetime.utcnow()
    message = Message(
        thread_id=thread_id,
        sender_id=message_in.sender_id,
        body=message_in.body,
        sent_at=now,
    )
    thread.updated_at = now
    session.add(message)
    session.add(thread)
    session.commit()
    session.refresh(message)
    return MessageRead.from_orm(message)


@router.get("/{thread_id}/messages", response_model=list[MessageRead])
def list_messages(thread_id: UUID, session: Session = Depends(get_session)) -> list[MessageRead]:
    """List messages in chronological order for a thread."""

    thread = session.get(ChatThread, thread_id)
    if not thread:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")

    messages = session.exec(
        select(Message).where(Message.thread_id == thread_id).order_by(Message.sent_at)
    ).all()
    return [MessageRead.from_orm(message) for message in messages]
