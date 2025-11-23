import math
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models import User, Venue, UserInterest, Friendship, InterestStatus


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers using haversine formula."""
    R = 6371.0  # Earth radius in kilometers

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance


def calculate_venue_score(
    db: Session,
    user_id: int,
    venue: Venue,
    user_location: Optional[Tuple[float, float]],
    friend_ids: List[int],
) -> float:
    """
    Calculate score for a venue based on:
    - Distance from user location (if provided)
    - User's previous interest
    - Popularity among friends
    """
    score = 0.0

    # Distance component (closer is better, max score 50 for very close venues)
    if user_location:
        distance = haversine_distance(
            user_location[0], user_location[1], venue.latitude, venue.longitude
        )
        # Exponential decay: closer venues get much higher scores
        # Distance in km: 0-1km=50pts, 1-5km=30-10pts, 5-10km=5-1pts, >10km=<1pt
        distance_score = 50 * math.exp(-distance / 2.0)
        score += distance_score

    # User's previous interest component (10 points if previously interested)
    user_interest = (
        db.query(UserInterest)
        .filter(
            and_(
                UserInterest.user_id == user_id,
                UserInterest.venue_id == venue.id,
                UserInterest.status.in_([InterestStatus.INTERESTED, InterestStatus.CONFIRMED]),
            )
        )
        .first()
    )
    if user_interest:
        score += 10.0

    # Popularity among friends component (5 points per interested friend)
    if friend_ids:
        interested_friends_count = (
            db.query(func.count(UserInterest.id))
            .filter(
                and_(
                    UserInterest.venue_id == venue.id,
                    UserInterest.user_id.in_(friend_ids),
                    UserInterest.status.in_([InterestStatus.INTERESTED, InterestStatus.CONFIRMED]),
                )
            )
            .scalar()
        )
        score += interested_friends_count * 5.0

    return score


def calculate_person_compatibility(
    db: Session, user_id: int, candidate_id: int, venue_id: int, friendship_strength: float
) -> float:
    """
    Calculate compatibility score for a person based on:
    - Friendship strength
    - Shared interested venues
    """
    score = 0.0

    # Friendship strength component (0-50 points based on strength)
    score += friendship_strength * 10.0

    # Shared interests component (count venues both users are interested in)
    user_interested_venues = (
        db.query(UserInterest.venue_id)
        .filter(
            and_(
                UserInterest.user_id == user_id,
                UserInterest.status.in_([InterestStatus.INTERESTED, InterestStatus.CONFIRMED]),
            )
        )
        .subquery()
    )

    candidate_interested_venues = (
        db.query(UserInterest.venue_id)
        .filter(
            and_(
                UserInterest.user_id == candidate_id,
                UserInterest.status.in_([InterestStatus.INTERESTED, InterestStatus.CONFIRMED]),
            )
        )
        .subquery()
    )

    shared_venues_count = (
        db.query(func.count())
        .select_from(user_interested_venues)
        .join(
            candidate_interested_venues,
            user_interested_venues.c.venue_id == candidate_interested_venues.c.venue_id,
        )
        .scalar()
    )

    score += shared_venues_count * 3.0

    # Bonus if candidate is interested in this specific venue
    candidate_interested_in_venue = (
        db.query(UserInterest)
        .filter(
            and_(
                UserInterest.user_id == candidate_id,
                UserInterest.venue_id == venue_id,
                UserInterest.status.in_([InterestStatus.INTERESTED, InterestStatus.CONFIRMED]),
            )
        )
        .first()
    )
    if candidate_interested_in_venue:
        score += 20.0

    return score


def get_recommendations_for_user(
    db: Session, user_id: int, user_location: Optional[Tuple[float, float]] = None
):
    """
    Generate venue and people recommendations for a user.

    Returns a list of venues with scores and recommended people for each venue.
    """
    # Get user's friends
    friendships = db.query(Friendship).filter(Friendship.user_id == user_id).all()
    friend_ids = [f.friend_id for f in friendships]
    friendship_map = {f.friend_id: f.strength for f in friendships}

    # Get all venues
    venues = db.query(Venue).all()

    recommendations = []

    for venue in venues:
        # Calculate venue score
        venue_score = calculate_venue_score(db, user_id, venue, user_location, friend_ids)

        # Get recommended people for this venue
        recommended_people = []

        for friend_id in friend_ids:
            friend = db.query(User).filter(User.id == friend_id).first()
            if not friend:
                continue

            friendship_strength = friendship_map.get(friend_id, 1.0)
            compatibility_score = calculate_person_compatibility(
                db, user_id, friend_id, venue.id, friendship_strength
            )

            recommended_people.append(
                {"user": friend, "compatibility_score": compatibility_score}
            )

        # Sort recommended people by compatibility score descending
        recommended_people.sort(key=lambda x: x["compatibility_score"], reverse=True)

        recommendations.append(
            {
                "venue": venue,
                "score": venue_score,
                "recommended_people": recommended_people[:5],  # Top 5 people
            }
        )

    # Sort venues by score descending
    recommendations.sort(key=lambda x: x["score"], reverse=True)

    return recommendations
