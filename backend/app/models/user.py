from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Marketplace user profile."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    email: str = Field(index=True, sa_column_kwargs={"unique": True})
    display_name: str = Field(index=True)
    bio: Optional[str] = None
    favorite_plants: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    home_city: Optional[str] = None
    home_state: Optional[str] = None
    country_code: Optional[str] = Field(default="US", max_length=2)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    radius_miles: int = Field(default=10, ge=1, le=200)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
