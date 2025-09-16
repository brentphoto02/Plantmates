from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Session, select

from ..models import Match
from ..models.enums import MatchStatus


@dataclass
class MatchOutcome:
    """Result of a like/pass interaction."""

    record: Match
    reciprocal: Optional[Match]
    is_mutual: bool


def _get_match(
    session: Session,
    listing_id: UUID,
    user_id: UUID,
    target_user_id: UUID,
) -> Optional[Match]:
    statement = select(Match).where(
        Match.listing_id == listing_id,
        Match.user_id == user_id,
        Match.target_user_id == target_user_id,
    )
    return session.exec(statement).first()


def like_listing(
    session: Session,
    *,
    listing_id: UUID,
    user_id: UUID,
    target_user_id: UUID,
) -> MatchOutcome:
    """Like a listing and promote to a match if the feeling is mutual."""

    match = _get_match(session, listing_id, user_id, target_user_id)
    now = datetime.utcnow()
    if match is None:
        match = Match(
            listing_id=listing_id,
            user_id=user_id,
            target_user_id=target_user_id,
            status=MatchStatus.liked,
            created_at=now,
            updated_at=now,
        )
        session.add(match)
    else:
        match.status = MatchStatus.liked
        match.updated_at = now

    reciprocal = _get_match(session, listing_id, target_user_id, user_id)
    is_mutual = False
    if reciprocal and reciprocal.status in {MatchStatus.liked, MatchStatus.matched}:
        match.status = MatchStatus.matched
        match.updated_at = now
        reciprocal.status = MatchStatus.matched
        reciprocal.updated_at = now
        is_mutual = True
        session.add(reciprocal)

    session.add(match)
    session.commit()
    session.refresh(match)
    if reciprocal:
        session.refresh(reciprocal)
    return MatchOutcome(record=match, reciprocal=reciprocal, is_mutual=is_mutual)


def pass_listing(
    session: Session,
    *,
    listing_id: UUID,
    user_id: UUID,
    target_user_id: UUID,
) -> MatchOutcome:
    """Record that a user passed on a listing."""

    match = _get_match(session, listing_id, user_id, target_user_id)
    now = datetime.utcnow()
    if match is None:
        match = Match(
            listing_id=listing_id,
            user_id=user_id,
            target_user_id=target_user_id,
            status=MatchStatus.passed,
            created_at=now,
            updated_at=now,
        )
        session.add(match)
    else:
        match.status = MatchStatus.passed
        match.updated_at = now

    session.add(match)
    session.commit()
    session.refresh(match)
    return MatchOutcome(record=match, reciprocal=None, is_mutual=False)
