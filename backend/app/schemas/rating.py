from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel


class RatingCreate(SQLModel):
    """Payload for submitting a rating after a swap."""

    swap_id: UUID
    reviewer_id: UUID
    reviewee_id: UUID
    reliability_score: int = Field(ge=1, le=5)
    plant_health_score: int = Field(ge=1, le=5)
    comments: Optional[str] = Field(default=None, max_length=500)


class RatingRead(RatingCreate):
    """Rating representation returned by the API."""

    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class RatingSummary(SQLModel):
    """Aggregate rating statistics for a user."""

    reviewee_id: UUID
    total_ratings: int
    average_reliability: Optional[float] = None
    average_plant_health: Optional[float] = None
