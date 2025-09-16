from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlmodel import Session, select

from ..db.session import get_session
from ..models import Listing, Swap
from ..models.enums import SwapStatus
from ..schemas import SwapCreate, SwapRead, SwapStatusUpdate

router = APIRouter(prefix="/swaps", tags=["swaps"])


@router.post("/", response_model=SwapRead, status_code=status.HTTP_201_CREATED)
def create_swap(swap_in: SwapCreate, session: Session = Depends(get_session)) -> SwapRead:
    """Create a swap request for a listing."""

    listing = session.get(Listing, swap_in.listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    if listing.owner_id == swap_in.requester_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot create a swap with yourself")

    existing = session.exec(
        select(Swap).where(
            Swap.listing_id == swap_in.listing_id,
            Swap.requester_id == swap_in.requester_id,
            Swap.status != SwapStatus.canceled,
        )
    ).first()
    if existing:
        return SwapRead.from_orm(existing)

    now = datetime.utcnow()
    swap = Swap(
        listing_id=swap_in.listing_id,
        requester_id=swap_in.requester_id,
        owner_id=listing.owner_id,
        status=SwapStatus.pending,
        requested_at=now,
        updated_at=now,
    )
    session.add(swap)
    session.commit()
    session.refresh(swap)
    return SwapRead.from_orm(swap)


@router.get("/", response_model=list[SwapRead])
def list_swaps(
    *,
    session: Session = Depends(get_session),
    user_id: Optional[UUID] = Query(default=None),
    listing_id: Optional[UUID] = Query(default=None),
    status_filter: Optional[SwapStatus] = Query(default=None),
) -> list[SwapRead]:
    """List swaps for a user or listing."""

    statement = select(Swap)
    if user_id:
        statement = statement.where(or_(Swap.requester_id == user_id, Swap.owner_id == user_id))
    if listing_id:
        statement = statement.where(Swap.listing_id == listing_id)
    if status_filter:
        statement = statement.where(Swap.status == status_filter)

    swaps = session.exec(statement).all()
    swaps.sort(key=lambda swap: swap.updated_at, reverse=True)
    return [SwapRead.from_orm(swap) for swap in swaps]


@router.get("/{swap_id}", response_model=SwapRead)
def get_swap(swap_id: UUID, session: Session = Depends(get_session)) -> SwapRead:
    """Retrieve a swap by id."""

    swap = session.get(Swap, swap_id)
    if not swap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Swap not found")
    return SwapRead.from_orm(swap)


@router.post("/{swap_id}/status", response_model=SwapRead)
def update_swap_status(
    swap_id: UUID,
    status_in: SwapStatusUpdate,
    session: Session = Depends(get_session),
) -> SwapRead:
    """Update the lifecycle status of a swap."""

    swap = session.get(Swap, swap_id)
    if not swap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Swap not found")

    if status_in.actor_id not in {swap.requester_id, swap.owner_id}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Actor not part of swap")

    now = datetime.utcnow()
    swap.status = status_in.status
    swap.updated_at = now

    if status_in.status == SwapStatus.agreed:
        swap.agreed_at = now
    elif status_in.status == SwapStatus.completed:
        swap.completed_at = now
    elif status_in.status in {SwapStatus.canceled, SwapStatus.no_show}:
        swap.canceled_at = now
        swap.cancellation_reason = status_in.note

    session.add(swap)
    session.commit()
    session.refresh(swap)
    return SwapRead.from_orm(swap)
