from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.models import Venue as VenueModel
from app.schemas import Venue, VenueCreate
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/venues", tags=["venues"])


@router.post("", response_model=Venue, status_code=201)
def create_venue(venue: VenueCreate, db: Session = Depends(get_db)):
    """Create a new venue."""
    db_venue = VenueModel(**venue.model_dump())
    db.add(db_venue)
    db.commit()
    db.refresh(db_venue)

    logger.info(f"Created venue {db_venue.id}", extra={"venue_id": db_venue.id})
    return db_venue


@router.get("", response_model=List[Venue])
def list_venues(
    category: Optional[str] = Query(None),
    min_lat: Optional[float] = Query(None),
    max_lat: Optional[float] = Query(None),
    min_lon: Optional[float] = Query(None),
    max_lon: Optional[float] = Query(None),
    db: Session = Depends(get_db),
):
    """
    List venues with optional filters.

    Filters:
    - category: Filter by venue category
    - min_lat, max_lat, min_lon, max_lon: Bounding box for location filtering
    """
    query = db.query(VenueModel)

    if category:
        query = query.filter(VenueModel.category == category)

    if min_lat is not None:
        query = query.filter(VenueModel.latitude >= min_lat)
    if max_lat is not None:
        query = query.filter(VenueModel.latitude <= max_lat)
    if min_lon is not None:
        query = query.filter(VenueModel.longitude >= min_lon)
    if max_lon is not None:
        query = query.filter(VenueModel.longitude <= max_lon)

    venues = query.all()
    return venues


@router.get("/{venue_id}", response_model=Venue)
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    """Get a specific venue."""
    venue = db.query(VenueModel).filter(VenueModel.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue
