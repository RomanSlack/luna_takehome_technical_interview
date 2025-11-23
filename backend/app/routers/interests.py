from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from datetime import datetime, timedelta
from app.db import get_db
from app.models import (
    User as UserModel,
    Venue as VenueModel,
    UserInterest as UserInterestModel,
    InterestStatus,
)
from app.schemas import UserInterest, UserInterestCreate
from app.services.agent import auto_create_reservation_if_ready
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["interests"])


@router.get("/{user_id}/interests", response_model=List[UserInterest])
def get_user_interests(user_id: int, db: Session = Depends(get_db)):
    """Get all interests for a user."""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    interests = db.query(UserInterestModel).filter(UserInterestModel.user_id == user_id).all()
    return interests


@router.post("/{user_id}/interests", response_model=UserInterest, status_code=201)
def create_or_update_interest(
    user_id: int, interest: UserInterestCreate, db: Session = Depends(get_db)
):
    """Create or update a user's interest in a venue."""
    # Verify user exists
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify venue exists
    venue = db.query(VenueModel).filter(VenueModel.id == interest.venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    # Check if interest already exists
    existing_interest = (
        db.query(UserInterestModel)
        .filter(
            and_(
                UserInterestModel.user_id == user_id,
                UserInterestModel.venue_id == interest.venue_id,
            )
        )
        .first()
    )

    if existing_interest:
        # Update existing interest
        existing_interest.status = interest.status
        db.commit()
        db.refresh(existing_interest)
        logger.info(
            f"Updated interest for user {user_id} in venue {interest.venue_id} to {interest.status}",
            extra={"user_id": user_id, "venue_id": interest.venue_id},
        )
        result_interest = existing_interest
    else:
        # Create new interest
        db_interest = UserInterestModel(
            user_id=user_id,
            venue_id=interest.venue_id,
            status=interest.status,
        )
        db.add(db_interest)
        db.commit()
        db.refresh(db_interest)
        logger.info(
            f"Created interest for user {user_id} in venue {interest.venue_id} with status {interest.status}",
            extra={"user_id": user_id, "venue_id": interest.venue_id},
        )
        result_interest = db_interest

    # If status is CONFIRMED, trigger agent to check for auto-reservation
    if interest.status == InterestStatus.CONFIRMED:
        # Get all users who have confirmed interest in this venue
        confirmed_users = (
            db.query(UserInterestModel)
            .filter(
                and_(
                    UserInterestModel.venue_id == interest.venue_id,
                    UserInterestModel.status == InterestStatus.CONFIRMED,
                )
            )
            .all()
        )

        confirmed_user_ids = [ui.user_id for ui in confirmed_users]

        # If 2 or more users confirmed, try to create reservation
        if len(confirmed_user_ids) >= 2:
            # Set reservation time to tomorrow at 7 PM
            reservation_time = datetime.now() + timedelta(days=1)
            reservation_time = reservation_time.replace(hour=19, minute=0, second=0, microsecond=0)

            agent_result = auto_create_reservation_if_ready(
                db=db,
                venue_id=interest.venue_id,
                user_ids=confirmed_user_ids,
                time=reservation_time,
                creator_user_id=user_id,
            )

            if agent_result["success"]:
                logger.info(
                    f"Auto-created reservation for venue {interest.venue_id}",
                    extra={"venue_id": interest.venue_id, "user_count": len(confirmed_user_ids)},
                )
            else:
                logger.info(
                    f"Agent did not create reservation: {agent_result['message']}",
                    extra={"venue_id": interest.venue_id},
                )

    return result_interest
