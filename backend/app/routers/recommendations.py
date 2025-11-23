from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db import get_db
from app.models import User as UserModel
from app.schemas import RecommendationsResponse
from app.services.recommendation import get_recommendations_for_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{user_id}", response_model=RecommendationsResponse)
def get_recommendations(
    user_id: int,
    lat: Optional[float] = Query(None, description="User's current latitude"),
    lon: Optional[float] = Query(None, description="User's current longitude"),
    db: Session = Depends(get_db),
):
    """
    Get personalized venue and people recommendations for a user.

    Query parameters:
    - lat: User's current latitude (optional)
    - lon: User's current longitude (optional)

    Returns ranked venues with scores and recommended people for each venue.
    """
    # Verify user exists
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate location parameters
    user_location = None
    if lat is not None and lon is not None:
        if not (-90 <= lat <= 90):
            raise HTTPException(status_code=422, detail="Latitude must be between -90 and 90")
        if not (-180 <= lon <= 180):
            raise HTTPException(status_code=422, detail="Longitude must be between -180 and 180")
        user_location = (lat, lon)
    elif lat is not None or lon is not None:
        raise HTTPException(
            status_code=422, detail="Both latitude and longitude must be provided together"
        )

    # Get recommendations
    recommendations = get_recommendations_for_user(db, user_id, user_location)

    logger.info(
        f"Generated {len(recommendations)} recommendations for user {user_id}",
        extra={"user_id": user_id},
    )

    return {"recommended_venues": recommendations}
