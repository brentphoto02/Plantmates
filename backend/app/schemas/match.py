from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel

from ..models.enums import MatchStatus


class MatchBase(SQLModel):
    """Shared match fields."""

    listing_id: UUID
    user_id: UUID
    target_user_id: UUID
    status: MatchStatus = Field(default=MatchStatus.liked)


class MatchRead(MatchBase):
    """Match representation returned to clients."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    is_mutual: bool = False

    class Config:
        orm_mode = True


class MatchActionRequest(SQLModel):
    """Request payload for performing match actions."""

    user_id: UUID
    target_user_id: Optional[UUID] = None


class MatchListResponse(SQLModel):
    """Collection wrapper for match responses."""

    items: list[MatchRead]
    total: int
