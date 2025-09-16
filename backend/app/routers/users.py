from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from ..core.config import settings
from ..db.session import get_session
from ..models import User
from ..schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, session: Session = Depends(get_session)) -> UserRead:
    """Create a new PlantMates user profile."""

    existing = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=user_in.email,
        display_name=user_in.display_name,
        bio=user_in.bio,
        favorite_plants=user_in.favorite_plants,
        home_city=user_in.home_city,
        home_state=user_in.home_state,
        country_code=user_in.country_code or "US",
        latitude=user_in.latitude,
        longitude=user_in.longitude,
        radius_miles=user_in.radius_miles or settings.default_radius_miles,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/", response_model=list[UserRead])
def list_users(
    *,
    session: Session = Depends(get_session),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[UserRead]:
    """Return a simple paginated list of users."""

    statement = select(User).offset(offset).limit(limit)
    users = session.exec(statement).all()
    return list(users)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: UUID, session: Session = Depends(get_session)) -> UserRead:
    """Retrieve a user profile by id."""

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    session: Session = Depends(get_session),
) -> UserRead:
    """Apply partial updates to a user profile."""

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = user_in.dict(exclude_unset=True)
    for field_name, value in update_data.items():
        setattr(user, field_name, value)
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, session: Session = Depends(get_session)) -> None:
    """Delete a user profile. Soft-deletion can be introduced later."""

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    session.delete(user)
    session.commit()
