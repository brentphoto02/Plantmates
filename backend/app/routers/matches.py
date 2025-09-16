from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlmodel import Session, select

from ..db.session import get_session
from ..models import Listing, Match
from ..models.enums import MatchStatus
from ..schemas import MatchActionRequest, MatchListResponse, MatchRead
from ..services.matching import like_listing as like_service
from ..services.matching import pass_listing as pass_service

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/{listing_id}/like", response_model=MatchRead)
def like_listing_endpoint(
    listing_id: UUID,
    action: MatchActionRequest,
    session: Session = Depends(get_session),
) -> MatchRead:
    """Like a listing and create a match when mutual."""

    listing = session.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    target_user_id = action.target_user_id or listing.owner_id
    if target_user_id == action.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot like your own listing")

    outcome = like_service(
        session,
        listing_id=listing_id,
        user_id=action.user_id,
        target_user_id=target_user_id,
    )
    response = MatchRead.from_orm(outcome.record)
    response.is_mutual = outcome.is_mutual
    return response


@router.post("/{listing_id}/pass", response_model=MatchRead)
def pass_listing_endpoint(
    listing_id: UUID,
    action: MatchActionRequest,
    session: Session = Depends(get_session),
) -> MatchRead:
    """Record that a user passed on a listing."""

    listing = session.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    target_user_id = action.target_user_id or listing.owner_id
    if target_user_id == action.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot pass on your own listing")

    outcome = pass_service(
        session,
        listing_id=listing_id,
        user_id=action.user_id,
        target_user_id=target_user_id,
    )
    response = MatchRead.from_orm(outcome.record)
    response.is_mutual = False
    return response


@router.get("/", response_model=MatchListResponse)
def list_matches(
    *,
    session: Session = Depends(get_session),
    user_id: UUID = Query(...),
    status_filter: Optional[MatchStatus] = Query(default=None),
    include_incoming: bool = Query(default=True),
) -> MatchListResponse:
    """Return matches for a user, optionally including incoming requests."""

    conditions = [Match.user_id == user_id]
    if include_incoming:
        conditions.append(Match.target_user_id == user_id)
    if len(conditions) == 1:
        statement = select(Match).where(conditions[0])
    else:
        statement = select(Match).where(or_(*conditions))

    results = session.exec(statement).all()
    items: list[MatchRead] = []
    for match in results:
        if status_filter and match.status != status_filter:
            continue
        match_read = MatchRead.from_orm(match)
        match_read.is_mutual = match.status == MatchStatus.matched
        items.append(match_read)
    return MatchListResponse(items=items, total=len(items))
