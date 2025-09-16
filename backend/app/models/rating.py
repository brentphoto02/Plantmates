from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Rating(SQLModel, table=True):
    """Post-swap rating for trust signals."""

    __tablename__ = "ratings"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    swap_id: UUID = Field(foreign_key="swaps.id", index=True)
    reviewer_id: UUID = Field(foreign_key="users.id", index=True)
    reviewee_id: UUID = Field(foreign_key="users.id", index=True)
    reliability_score: int = Field(ge=1, le=5)
    plant_health_score: int = Field(ge=1, le=5)
    comments: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
