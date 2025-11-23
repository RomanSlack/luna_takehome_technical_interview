from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import (
    UserInterest,
    Reservation,
    ReservationParticipant,
    InterestStatus,
    ReservationStatus,
    ParticipantStatus,
)
import logging

logger = logging.getLogger(__name__)


def auto_create_reservation_if_ready(
    db: Session,
    venue_id: int,
    user_ids: List[int],
    time: datetime,
    creator_user_id: int,
) -> dict:
    """
    Automatically create a reservation if all users have confirmed interest.

    Args:
        db: Database session
        venue_id: ID of the venue
        user_ids: List of user IDs who should be participating
        time: Desired reservation time
        creator_user_id: User who initiated the reservation

    Returns:
        dict with keys:
            - success: bool
            - message: str
            - reservation: Optional[Reservation]
    """
    # Check if all users have confirmed interest in the venue
    confirmed_users = []
    missing_confirmations = []

    for user_id in user_ids:
        user_interest = (
            db.query(UserInterest)
            .filter(
                and_(
                    UserInterest.user_id == user_id,
                    UserInterest.venue_id == venue_id,
                )
            )
            .first()
        )

        if user_interest and user_interest.status == InterestStatus.CONFIRMED:
            confirmed_users.append(user_id)
        else:
            missing_confirmations.append(user_id)

    # If not all users have confirmed, return failure
    if missing_confirmations:
        logger.info(
            f"Cannot create reservation: users {missing_confirmations} have not confirmed interest in venue {venue_id}"
        )
        return {
            "success": False,
            "message": f"Waiting for users {missing_confirmations} to confirm interest",
            "reservation": None,
        }

    # Check if a reservation already exists for this venue and time window (within 30 minutes)
    time_window_start = time - timedelta(minutes=30)
    time_window_end = time + timedelta(minutes=30)

    existing_reservation = (
        db.query(Reservation)
        .filter(
            and_(
                Reservation.venue_id == venue_id,
                Reservation.time >= time_window_start,
                Reservation.time <= time_window_end,
                Reservation.status != ReservationStatus.CANCELLED,
            )
        )
        .first()
    )

    if existing_reservation:
        # Check if all users are already participants
        existing_participant_ids = {p.user_id for p in existing_reservation.participants}
        all_users_included = all(uid in existing_participant_ids for uid in user_ids)

        if all_users_included:
            logger.info(
                f"Reservation {existing_reservation.id} already exists with all participants"
            )
            return {
                "success": True,
                "message": "Reservation already exists",
                "reservation": existing_reservation,
            }

    # All users confirmed, create the reservation
    new_reservation = Reservation(
        venue_id=venue_id,
        created_by_user_id=creator_user_id,
        time=time,
        status=ReservationStatus.CONFIRMED,
    )

    db.add(new_reservation)
    db.flush()  # Get the reservation ID

    # Add all participants as ACCEPTED
    for user_id in user_ids:
        participant = ReservationParticipant(
            reservation_id=new_reservation.id,
            user_id=user_id,
            status=ParticipantStatus.ACCEPTED,
        )
        db.add(participant)

    db.commit()
    db.refresh(new_reservation)

    logger.info(
        f"Auto-created reservation {new_reservation.id} for venue {venue_id} at {time}",
        extra={"reservation_id": new_reservation.id},
    )

    return {
        "success": True,
        "message": "Reservation created successfully",
        "reservation": new_reservation,
    }


def check_and_confirm_reservation(db: Session, reservation_id: int) -> Optional[Reservation]:
    """
    Check if all participants have accepted and auto-confirm the reservation.

    Args:
        db: Database session
        reservation_id: ID of the reservation to check

    Returns:
        The reservation if updated, None otherwise
    """
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if not reservation:
        return None

    if reservation.status == ReservationStatus.CONFIRMED:
        return reservation

    # Check if all participants have accepted
    all_accepted = all(
        p.status == ParticipantStatus.ACCEPTED for p in reservation.participants
    )

    if all_accepted and len(reservation.participants) > 0:
        reservation.status = ReservationStatus.CONFIRMED
        db.commit()
        db.refresh(reservation)
        logger.info(
            f"Auto-confirmed reservation {reservation_id}",
            extra={"reservation_id": reservation_id},
        )
        return reservation

    return None
