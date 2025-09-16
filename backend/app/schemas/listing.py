from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel

from ..models.enums import TransactionType


class ListingBase(SQLModel):
    """Fields shared across listing representations."""

    title: str = Field(min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    species: Optional[str] = Field(default=None, max_length=120)
    transaction_types: list[TransactionType] = Field(default_factory=list, min_items=1)
    price_cents: Optional[int] = Field(default=None, ge=0)
    preferred_trades: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    photo_urls: list[str] = Field(default_factory=list)
    quantity: int = Field(default=1, ge=1)
    condition_notes: Optional[str] = Field(default=None, max_length=500)
    propagation_notes: Optional[str] = Field(default=None, max_length=500)
    pickup_area: Optional[str] = Field(default=None, max_length=200)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    available_start: Optional[datetime] = None
    available_end: Optional[datetime] = None
    is_active: Optional[bool] = Field(default=True)


class ListingCreate(ListingBase):
    """Payload for creating a new listing."""

    owner_id: UUID


class ListingUpdate(SQLModel):
    """Payload for updating an existing listing."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    species: Optional[str] = Field(default=None, max_length=120)
    transaction_types: Optional[list[TransactionType]] = None
    price_cents: Optional[int] = Field(default=None, ge=0)
    preferred_trades: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    photo_urls: Optional[list[str]] = None
    quantity: Optional[int] = Field(default=None, ge=1)
    condition_notes: Optional[str] = Field(default=None, max_length=500)
    propagation_notes: Optional[str] = Field(default=None, max_length=500)
    pickup_area: Optional[str] = Field(default=None, max_length=200)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    available_start: Optional[datetime] = None
    available_end: Optional[datetime] = None
    is_active: Optional[bool] = None


class ListingRead(ListingBase):
    """Listing representation for API responses."""

    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    distance_miles: Optional[float] = None

    class Config:
        orm_mode = True


class ListingListResponse(SQLModel):
    """Paginated collection of listings."""

    items: list[ListingRead]
    total: int
