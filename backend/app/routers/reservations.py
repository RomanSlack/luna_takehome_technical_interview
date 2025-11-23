from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List
from datetime import datetime
from app.db import get_db
from app.models import (
    User as UserModel,
    Venue as VenueModel,
    Reservation as ReservationModel,
    ReservationParticipant as ParticipantModel,
    ParticipantStatus,
)
from app.schemas import Reservation, ReservationCreate, ReservationAccept, AgentResult
from app.services.agent import auto_create_reservation_if_ready, check_and_confirm_reservation
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.post("", response_model=Reservation, status_code=201)
def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    """
    Create a new reservation.

    This will create a pending reservation and invite all specified participants.
    """
    # Verify venue exists
    venue = db.query(VenueModel).filter(VenueModel.id == reservation.venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    # Verify all participant users exist
    if not reservation.participant_user_ids:
        raise HTTPException(status_code=422, detail="At least one participant is required")

    for user_id in reservation.participant_user_ids:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    # Create reservation (first participant is the creator)
    creator_id = reservation.participant_user_ids[0]

    db_reservation = ReservationModel(
        venue_id=reservation.venue_id,
        created_by_user_id=creator_id,
        time=reservation.time,
    )

    db.add(db_reservation)
    db.flush()

    # Add participants
    for user_id in reservation.participant_user_ids:
        participant = ParticipantModel(
            reservation_id=db_reservation.id,
            user_id=user_id,
            status=ParticipantStatus.INVITED,
        )
        db.add(participant)

    db.commit()
    db.refresh(db_reservation)

    logger.info(
        f"Created reservation {db_reservation.id} for venue {reservation.venue_id}",
        extra={"reservation_id": db_reservation.id, "venue_id": reservation.venue_id},
    )

    return db_reservation


@router.post("/accept", response_model=AgentResult)
def accept_reservation(accept: ReservationAccept, db: Session = Depends(get_db)):
    """
    Accept a reservation invitation.

    This updates the participant's status and may trigger automatic reservation confirmation
    if all participants have accepted.
    """
    # Verify reservation exists
    reservation = (
        db.query(ReservationModel).filter(ReservationModel.id == accept.reservation_id).first()
    )
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Verify user exists
    user = db.query(UserModel).filter(UserModel.id == accept.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Find participant record
    participant = (
        db.query(ParticipantModel)
        .filter(
            and_(
                ParticipantModel.reservation_id == accept.reservation_id,
                ParticipantModel.user_id == accept.user_id,
            )
        )
        .first()
    )

    if not participant:
        raise HTTPException(
            status_code=404, detail="User is not a participant in this reservation"
        )

    # Update participant status
    participant.status = ParticipantStatus.ACCEPTED
    db.commit()

    logger.info(
        f"User {accept.user_id} accepted reservation {accept.reservation_id}",
        extra={"user_id": accept.user_id, "reservation_id": accept.reservation_id},
    )

    # Check if all participants have accepted and auto-confirm
    updated_reservation = check_and_confirm_reservation(db, accept.reservation_id)

    if updated_reservation:
        return {
            "success": True,
            "message": "Reservation accepted and confirmed",
            "reservation": updated_reservation,
        }
    else:
        db.refresh(reservation)
        return {
            "success": True,
            "message": "Reservation accepted, waiting for other participants",
            "reservation": reservation,
        }


@router.get("/{user_id}", response_model=List[Reservation])
def get_user_reservations(user_id: int, db: Session = Depends(get_db)):
    """Get all reservations for a user (as creator or participant)."""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get reservations where user is creator or participant
    reservations = (
        db.query(ReservationModel)
        .join(ParticipantModel)
        .filter(
            or_(
                ReservationModel.created_by_user_id == user_id,
                and_(
                    ParticipantModel.reservation_id == ReservationModel.id,
                    ParticipantModel.user_id == user_id,
                ),
            )
        )
        .distinct()
        .all()
    )

    return reservations
