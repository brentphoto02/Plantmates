from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from .enums import SwapStatus


class Swap(SQLModel, table=True):
    """Represents the lifecycle of a swap or sale agreement."""

    __tablename__ = "swaps"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    listing_id: UUID = Field(foreign_key="listings.id", index=True)
    requester_id: UUID = Field(foreign_key="users.id", index=True)
    owner_id: UUID = Field(foreign_key="users.id", index=True)
    status: SwapStatus = Field(default=SwapStatus.pending, index=True)
    requested_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    agreed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
