from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Fields shared across user representations."""

    display_name: str = Field(min_length=1, max_length=80)
    bio: Optional[str] = Field(default=None, max_length=500)
    favorite_plants: list[str] = Field(default_factory=list)
    home_city: Optional[str] = Field(default=None, max_length=120)
    home_state: Optional[str] = Field(default=None, max_length=120)
    country_code: Optional[str] = Field(default="US", max_length=2)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    radius_miles: Optional[int] = Field(default=None, ge=1, le=200)


class UserCreate(UserBase):
    """Payload for creating a new user."""

    email: EmailStr


class UserUpdate(SQLModel):
    """Payload for partially updating an existing user."""

    display_name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    bio: Optional[str] = Field(default=None, max_length=500)
    favorite_plants: Optional[list[str]] = None
    home_city: Optional[str] = Field(default=None, max_length=120)
    home_state: Optional[str] = Field(default=None, max_length=120)
    country_code: Optional[str] = Field(default=None, max_length=2)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    radius_miles: Optional[int] = Field(default=None, ge=1, le=200)


class UserRead(UserBase):
    """User representation returned by the API."""

    id: UUID
    email: EmailStr
    radius_miles: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
