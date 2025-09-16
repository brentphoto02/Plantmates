from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from .enums import MatchStatus


class Match(SQLModel, table=True):
    """Represents a like/pass relationship between two users for a listing."""

    __tablename__ = "matches"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    listing_id: UUID = Field(foreign_key="listings.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    target_user_id: UUID = Field(foreign_key="users.id", index=True)
    status: MatchStatus = Field(default=MatchStatus.liked, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
