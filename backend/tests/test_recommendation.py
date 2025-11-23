import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import User, Venue, UserInterest, Friendship, InterestStatus
from app.services.recommendation import (
    get_recommendations_for_user,
    haversine_distance,
    calculate_venue_score,
    calculate_person_compatibility,
)

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def seed_data(db):
    """Seed test data."""
    # Create users
    user1 = User(id=1, name="Alice", avatar_url="https://example.com/alice.jpg")
    user2 = User(id=2, name="Bob", avatar_url="https://example.com/bob.jpg")
    user3 = User(id=3, name="Charlie", avatar_url="https://example.com/charlie.jpg")

    db.add_all([user1, user2, user3])
    db.flush()

    # Create venues
    venue1 = Venue(
        id=1,
        name="Coffee Shop",
        category="cafe",
        address="123 Main St",
        latitude=40.7589,
        longitude=-73.9851,
    )
    venue2 = Venue(
        id=2,
        name="Italian Restaurant",
        category="restaurant",
        address="456 Park Ave",
        latitude=40.7614,
        longitude=-73.9776,
    )
    venue3 = Venue(
        id=3,
        name="Music Venue",
        category="entertainment",
        address="789 Broadway",
        latitude=40.7505,
        longitude=-73.9934,
    )

    db.add_all([venue1, venue2, venue3])
    db.flush()

    # Create friendships
    friendship1 = Friendship(user_id=1, friend_id=2, strength=5.0)
    friendship2 = Friendship(user_id=1, friend_id=3, strength=3.0)

    db.add_all([friendship1, friendship2])
    db.flush()

    # Create interests
    interest1 = UserInterest(user_id=2, venue_id=1, status=InterestStatus.INTERESTED)
    interest2 = UserInterest(user_id=2, venue_id=2, status=InterestStatus.CONFIRMED)
    interest3 = UserInterest(user_id=3, venue_id=1, status=InterestStatus.INTERESTED)

    db.add_all([interest1, interest2, interest3])
    db.commit()

    return {
        "users": [user1, user2, user3],
        "venues": [venue1, venue2, venue3],
        "friendships": [friendship1, friendship2],
        "interests": [interest1, interest2, interest3],
    }


def test_haversine_distance():
    """Test haversine distance calculation."""
    # Distance between Times Square (40.7589, -73.9851) and Central Park (40.7829, -73.9654)
    distance = haversine_distance(40.7589, -73.9851, 40.7829, -73.9654)
    # Should be approximately 2.8 km
    assert 2.5 < distance < 3.1


def test_get_recommendations_returns_sorted_venues(db, seed_data):
    """Test that recommendations are returned sorted by score descending."""
    # User 1 at Times Square location
    user_location = (40.7589, -73.9851)
    recommendations = get_recommendations_for_user(db, user_id=1, user_location=user_location)

    assert len(recommendations) == 3
    # Verify scores are descending
    scores = [r["score"] for r in recommendations]
    assert scores == sorted(scores, reverse=True)


def test_venue_score_prioritizes_closer_venues(db, seed_data):
    """Test that closer venues get higher distance scores."""
    user_location = (40.7589, -73.9851)  # Times Square

    # Coffee Shop is very close to Times Square
    venue1 = db.query(Venue).filter(Venue.id == 1).first()
    score1 = calculate_venue_score(db, user_id=1, venue=venue1, user_location=user_location, friend_ids=[2, 3])

    # Music Venue is farther
    venue3 = db.query(Venue).filter(Venue.id == 3).first()
    score3 = calculate_venue_score(db, user_id=1, venue=venue3, user_location=user_location, friend_ids=[2, 3])

    # Coffee Shop should have higher score due to closer distance
    assert score1 > score3


def test_venue_score_includes_friend_interest(db, seed_data):
    """Test that venues with interested friends get higher scores."""
    # Coffee Shop has 2 interested friends (Bob and Charlie)
    venue1 = db.query(Venue).filter(Venue.id == 1).first()
    score1 = calculate_venue_score(db, user_id=1, venue=venue1, user_location=None, friend_ids=[2, 3])

    # Music Venue has no interested friends
    venue3 = db.query(Venue).filter(Venue.id == 3).first()
    score3 = calculate_venue_score(db, user_id=1, venue=venue3, user_location=None, friend_ids=[2, 3])

    # Coffee Shop should have higher score due to friend interest
    assert score1 > score3


def test_person_compatibility_includes_friendship_strength(db, seed_data):
    """Test that person compatibility considers friendship strength."""
    # Bob has friendship strength 5.0
    score_bob = calculate_person_compatibility(db, user_id=1, candidate_id=2, venue_id=1, friendship_strength=5.0)

    # Charlie has friendship strength 3.0
    score_charlie = calculate_person_compatibility(db, user_id=1, candidate_id=3, venue_id=1, friendship_strength=3.0)

    # Bob should have higher score due to stronger friendship
    assert score_bob > score_charlie


def test_person_compatibility_bonus_for_venue_interest(db, seed_data):
    """Test that candidates interested in the specific venue get a bonus."""
    # Bob is interested in Coffee Shop (venue 1)
    score_bob_venue1 = calculate_person_compatibility(db, user_id=1, candidate_id=2, venue_id=1, friendship_strength=5.0)

    # Bob is not interested in Music Venue (venue 3)
    score_bob_venue3 = calculate_person_compatibility(db, user_id=1, candidate_id=2, venue_id=3, friendship_strength=5.0)

    # Score for venue 1 should be higher due to Bob's interest
    assert score_bob_venue1 > score_bob_venue3


def test_recommendations_include_people_for_each_venue(db, seed_data):
    """Test that each venue recommendation includes recommended people."""
    recommendations = get_recommendations_for_user(db, user_id=1, user_location=None)

    for rec in recommendations:
        assert "venue" in rec
        assert "score" in rec
        assert "recommended_people" in rec
        assert isinstance(rec["recommended_people"], list)

        # Check structure of recommended people
        for person in rec["recommended_people"]:
            assert "user" in person
            assert "compatibility_score" in person
            assert isinstance(person["compatibility_score"], float)
