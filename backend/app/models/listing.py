from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from .enums import TransactionType


class Listing(SQLModel, table=True):
    """Marketplace listing for a plant or related item."""

    __tablename__ = "listings"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    owner_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(index=True)
    description: Optional[str] = None
    species: Optional[str] = Field(default=None, index=True)
    transaction_types: list[TransactionType] = Field(default_factory=list, sa_column=Column(JSON))
    price_cents: Optional[int] = Field(default=None, ge=0)
    preferred_trades: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    photo_urls: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    quantity: int = Field(default=1, ge=1)
    condition_notes: Optional[str] = None
    propagation_notes: Optional[str] = None
    pickup_area: Optional[str] = None
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    available_start: Optional[datetime] = None
    available_end: Optional[datetime] = None
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
