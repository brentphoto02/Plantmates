from __future__ import annotations

from statistics import mean
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from ..db.session import get_session
from ..models import Rating, Swap
from ..schemas import RatingCreate, RatingRead, RatingSummary

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.post("/", response_model=RatingRead, status_code=status.HTTP_201_CREATED)
def create_rating(rating_in: RatingCreate, session: Session = Depends(get_session)) -> RatingRead:
    """Create a rating for a completed swap."""

    swap = session.get(Swap, rating_in.swap_id)
    if not swap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Swap not found")
    if rating_in.reviewer_id not in {swap.requester_id, swap.owner_id}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reviewer not part of swap")
    if rating_in.reviewee_id not in {swap.requester_id, swap.owner_id}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reviewee not part of swap")
    if rating_in.reviewer_id == rating_in.reviewee_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot review yourself")

    existing = session.exec(
        select(Rating).where(
            Rating.swap_id == rating_in.swap_id,
            Rating.reviewer_id == rating_in.reviewer_id,
        )
    ).first()
    if existing:
        return RatingRead.from_orm(existing)

    rating = Rating(**rating_in.dict())
    session.add(rating)
    session.commit()
    session.refresh(rating)
    return RatingRead.from_orm(rating)


@router.get("/", response_model=list[RatingRead])
def list_ratings(
    *,
    session: Session = Depends(get_session),
    reviewee_id: Optional[UUID] = Query(default=None),
    reviewer_id: Optional[UUID] = Query(default=None),
    swap_id: Optional[UUID] = Query(default=None),
) -> list[RatingRead]:
    """List ratings filtered by reviewer, reviewee, or swap."""

    statement = select(Rating)
    if reviewee_id:
        statement = statement.where(Rating.reviewee_id == reviewee_id)
    if reviewer_id:
        statement = statement.where(Rating.reviewer_id == reviewer_id)
    if swap_id:
        statement = statement.where(Rating.swap_id == swap_id)

    ratings = session.exec(statement).all()
    ratings.sort(key=lambda rating: rating.created_at, reverse=True)
    return [RatingRead.from_orm(rating) for rating in ratings]


@router.get("/{user_id}/summary", response_model=RatingSummary)
def rating_summary(user_id: UUID, session: Session = Depends(get_session)) -> RatingSummary:
    """Return aggregate rating statistics for a user."""

    ratings = session.exec(select(Rating).where(Rating.reviewee_id == user_id)).all()
    if not ratings:
        return RatingSummary(
            reviewee_id=user_id,
            total_ratings=0,
            average_reliability=None,
            average_plant_health=None,
        )

    reliability_scores = [rating.reliability_score for rating in ratings]
    plant_health_scores = [rating.plant_health_score for rating in ratings]
    return RatingSummary(
        reviewee_id=user_id,
        total_ratings=len(ratings),
        average_reliability=round(mean(reliability_scores), 2),
        average_plant_health=round(mean(plant_health_scores), 2),
    )
