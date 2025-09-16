from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel

from ..models.enums import SwapStatus


class SwapBase(SQLModel):
    """Shared swap fields."""

    listing_id: UUID
    requester_id: UUID
    owner_id: UUID
    status: SwapStatus = Field(default=SwapStatus.pending)


class SwapCreate(SQLModel):
    """Payload for creating a new swap request."""

    listing_id: UUID
    requester_id: UUID


class SwapStatusUpdate(SQLModel):
    """Payload for updating swap status."""

    status: SwapStatus
    actor_id: UUID
    note: Optional[str] = Field(default=None, max_length=500)


class SwapRead(SwapBase):
    """Swap representation returned to clients."""

    id: UUID
    requested_at: datetime
    agreed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    updated_at: datetime

    class Config:
        orm_mode = True
