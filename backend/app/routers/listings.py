from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from ..core.config import settings
from ..db.session import get_session
from ..models import Listing, User
from ..models.enums import TransactionType
from ..schemas import ListingCreate, ListingListResponse, ListingRead, ListingUpdate
from ..services.geo import haversine_distance_miles

router = APIRouter(prefix="/listings", tags=["listings"])


@router.post("/", response_model=ListingRead, status_code=status.HTTP_201_CREATED)
def create_listing(listing_in: ListingCreate, session: Session = Depends(get_session)) -> ListingRead:
    """Create a new listing for a plant or related item."""

    owner = session.get(User, listing_in.owner_id)
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")

    listing = Listing(**listing_in.dict())
    session.add(listing)
    session.commit()
    session.refresh(listing)
    return ListingRead.from_orm(listing)


@router.get("/", response_model=ListingListResponse)
def list_listings(
    *,
    session: Session = Depends(get_session),
    owner_id: Optional[UUID] = Query(default=None),
    transaction_type: Optional[TransactionType] = Query(default=None),
    tags: Optional[list[str]] = Query(default=None),
    latitude: Optional[float] = Query(default=None, ge=-90, le=90),
    longitude: Optional[float] = Query(default=None, ge=-180, le=180),
    radius_miles: Optional[int] = Query(default=None, ge=1, le=settings.max_radius_miles),
    include_inactive: bool = Query(default=False),
    sort: Optional[str] = Query(default=None, regex="^(distance|newest|price_asc|price_desc)$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ListingListResponse:
    """Return listings with optional filtering, sorting, and distance calculations."""

    statement = select(Listing)
    if not include_inactive:
        statement = statement.where(Listing.is_active.is_(True))
    if owner_id:
        statement = statement.where(Listing.owner_id == owner_id)

    listings = session.exec(statement).all()

    filtered: list[tuple[ListingRead, Optional[float]]] = []
    tag_set = set(tags or [])

    for listing in listings:
        if transaction_type and transaction_type not in listing.transaction_types:
            continue
        if tag_set and not tag_set.issubset(set(listing.tags)):
            continue

        distance = haversine_distance_miles(latitude, longitude, listing.latitude, listing.longitude)
        if radius_miles and distance is not None and distance > radius_miles:
            continue

        listing_read = ListingRead.from_orm(listing)
        if distance is not None:
            listing_read.distance_miles = round(distance, 2)
        filtered.append((listing_read, distance))

    if sort == "distance" and latitude is not None and longitude is not None:
        filtered.sort(key=lambda item: item[1] if item[1] is not None else float("inf"))
    elif sort == "newest":
        filtered.sort(key=lambda item: item[0].created_at, reverse=True)
    elif sort == "price_asc":
        filtered.sort(key=lambda item: (item[0].price_cents is None, item[0].price_cents or 0))
    elif sort == "price_desc":
        filtered.sort(key=lambda item: (item[0].price_cents is None, -(item[0].price_cents or 0)))

    total = len(filtered)
    paginated = filtered[offset : offset + limit]
    items = [item[0] for item in paginated]
    return ListingListResponse(items=items, total=total)


@router.get("/{listing_id}", response_model=ListingRead)
def get_listing(listing_id: UUID, session: Session = Depends(get_session)) -> ListingRead:
    """Retrieve a listing by id."""

    listing = session.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    return ListingRead.from_orm(listing)


@router.patch("/{listing_id}", response_model=ListingRead)
def update_listing(
    listing_id: UUID,
    listing_in: ListingUpdate,
    session: Session = Depends(get_session),
) -> ListingRead:
    """Apply updates to a listing."""

    listing = session.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    update_data = listing_in.dict(exclude_unset=True)
    for field_name, value in update_data.items():
        setattr(listing, field_name, value)
    listing.updated_at = datetime.utcnow()
    session.add(listing)
    session.commit()
    session.refresh(listing)
    return ListingRead.from_orm(listing)


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_listing(listing_id: UUID, session: Session = Depends(get_session)) -> None:
    """Archive a listing instead of hard deleting to maintain history."""

    listing = session.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    listing.is_active = False
    listing.updated_at = datetime.utcnow()
    session.add(listing)
    session.commit()
