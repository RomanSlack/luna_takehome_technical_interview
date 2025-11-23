import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.main import app
from app.db import Base, get_db
from app.models import InterestStatus

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create a fresh database and test client for each test."""
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    yield client
    Base.metadata.drop_all(bind=engine)


def test_root_endpoint(client):
    """Test root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_user(client):
    """Test creating a user."""
    response = client.post(
        "/users",
        json={"name": "Alice", "avatar_url": "https://example.com/alice.jpg", "bio": "Test bio"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert data["id"] is not None


def test_list_users(client):
    """Test listing users."""
    # Create a user first
    client.post("/users", json={"name": "Alice"})
    client.post("/users", json={"name": "Bob"})

    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_user(client):
    """Test getting a specific user."""
    # Create a user
    create_response = client.post("/users", json={"name": "Alice"})
    user_id = create_response.json()["id"]

    # Get the user
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice"


def test_get_nonexistent_user(client):
    """Test getting a user that doesn't exist."""
    response = client.get("/users/999")
    assert response.status_code == 404


def test_create_venue(client):
    """Test creating a venue."""
    response = client.post(
        "/venues",
        json={
            "name": "Coffee Shop",
            "category": "cafe",
            "address": "123 Main St",
            "latitude": 40.7589,
            "longitude": -73.9851,
            "description": "Great coffee",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Coffee Shop"
    assert data["category"] == "cafe"


def test_list_venues_with_filters(client):
    """Test listing venues with category filter."""
    # Create venues
    client.post(
        "/venues",
        json={
            "name": "Coffee Shop",
            "category": "cafe",
            "address": "123 Main St",
            "latitude": 40.7589,
            "longitude": -73.9851,
        },
    )
    client.post(
        "/venues",
        json={
            "name": "Italian Restaurant",
            "category": "restaurant",
            "address": "456 Park Ave",
            "latitude": 40.7614,
            "longitude": -73.9776,
        },
    )

    # Filter by category
    response = client.get("/venues?category=cafe")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "cafe"


def test_create_interest(client):
    """Test creating a user interest."""
    # Create user and venue
    user_response = client.post("/users", json={"name": "Alice"})
    user_id = user_response.json()["id"]

    venue_response = client.post(
        "/venues",
        json={
            "name": "Coffee Shop",
            "category": "cafe",
            "address": "123 Main St",
            "latitude": 40.7589,
            "longitude": -73.9851,
        },
    )
    venue_id = venue_response.json()["id"]

    # Create interest
    response = client.post(
        f"/users/{user_id}/interests",
        json={"venue_id": venue_id, "status": "INTERESTED"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == user_id
    assert data["venue_id"] == venue_id
    assert data["status"] == "INTERESTED"


def test_update_interest(client):
    """Test updating an existing interest."""
    # Create user and venue
    user_response = client.post("/users", json={"name": "Alice"})
    user_id = user_response.json()["id"]

    venue_response = client.post(
        "/venues",
        json={
            "name": "Coffee Shop",
            "category": "cafe",
            "address": "123 Main St",
            "latitude": 40.7589,
            "longitude": -73.9851,
        },
    )
    venue_id = venue_response.json()["id"]

    # Create interest
    client.post(
        f"/users/{user_id}/interests",
        json={"venue_id": venue_id, "status": "INTERESTED"},
    )

    # Update interest
    response = client.post(
        f"/users/{user_id}/interests",
        json={"venue_id": venue_id, "status": "CONFIRMED"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "CONFIRMED"


def test_get_recommendations(client):
    """Test getting recommendations for a user."""
    # Create user
    user_response = client.post("/users", json={"name": "Alice"})
    user_id = user_response.json()["id"]

    # Create a venue
    client.post(
        "/venues",
        json={
            "name": "Coffee Shop",
            "category": "cafe",
            "address": "123 Main St",
            "latitude": 40.7589,
            "longitude": -73.9851,
        },
    )

    # Get recommendations
    response = client.get(f"/recommendations/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert "recommended_venues" in data
    assert isinstance(data["recommended_venues"], list)


def test_get_recommendations_with_location(client):
    """Test getting recommendations with user location."""
    # Create user
    user_response = client.post("/users", json={"name": "Alice"})
    user_id = user_response.json()["id"]

    # Create a venue
    client.post(
        "/venues",
        json={
            "name": "Coffee Shop",
            "category": "cafe",
            "address": "123 Main St",
            "latitude": 40.7589,
            "longitude": -73.9851,
        },
    )

    # Get recommendations with location
    response = client.get(f"/recommendations/{user_id}?lat=40.7589&lon=-73.9851")
    assert response.status_code == 200
    data = response.json()
    assert "recommended_venues" in data


def test_get_recommendations_invalid_location(client):
    """Test that invalid location parameters are rejected."""
    user_response = client.post("/users", json={"name": "Alice"})
    user_id = user_response.json()["id"]

    # Invalid latitude
    response = client.get(f"/recommendations/{user_id}?lat=999&lon=-73.9851")
    assert response.status_code == 422

    # Only one coordinate provided
    response = client.get(f"/recommendations/{user_id}?lat=40.7589")
    assert response.status_code == 422


def test_create_reservation(client):
    """Test creating a reservation."""
    # Create users
    user1_response = client.post("/users", json={"name": "Alice"})
    user1_id = user1_response.json()["id"]

    user2_response = client.post("/users", json={"name": "Bob"})
    user2_id = user2_response.json()["id"]

    # Create venue
    venue_response = client.post(
        "/venues",
        json={
            "name": "Coffee Shop",
            "category": "cafe",
            "address": "123 Main St",
            "latitude": 40.7589,
            "longitude": -73.9851,
        },
    )
    venue_id = venue_response.json()["id"]

    # Create reservation
    reservation_time = (datetime.utcnow() + timedelta(hours=2)).isoformat()
    response = client.post(
        "/reservations",
        json={
            "venue_id": venue_id,
            "time": reservation_time,
            "participant_user_ids": [user1_id, user2_id],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["venue_id"] == venue_id
    assert len(data["participants"]) == 2


def test_accept_reservation(client):
    """Test accepting a reservation invitation."""
    # Create users
    user1_response = client.post("/users", json={"name": "Alice"})
    user1_id = user1_response.json()["id"]

    user2_response = client.post("/users", json={"name": "Bob"})
    user2_id = user2_response.json()["id"]

    # Create venue
    venue_response = client.post(
        "/venues",
        json={
            "name": "Coffee Shop",
            "category": "cafe",
            "address": "123 Main St",
            "latitude": 40.7589,
            "longitude": -73.9851,
        },
    )
    venue_id = venue_response.json()["id"]

    # Create reservation
    reservation_time = (datetime.utcnow() + timedelta(hours=2)).isoformat()
    reservation_response = client.post(
        "/reservations",
        json={
            "venue_id": venue_id,
            "time": reservation_time,
            "participant_user_ids": [user1_id, user2_id],
        },
    )
    reservation_id = reservation_response.json()["id"]

    # Accept reservation
    response = client.post(
        "/reservations/accept",
        json={"reservation_id": reservation_id, "user_id": user1_id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "reservation" in data


def test_get_user_reservations(client):
    """Test getting reservations for a user."""
    # Create user
    user_response = client.post("/users", json={"name": "Alice"})
    user_id = user_response.json()["id"]

    # Create venue
    venue_response = client.post(
        "/venues",
        json={
            "name": "Coffee Shop",
            "category": "cafe",
            "address": "123 Main St",
            "latitude": 40.7589,
            "longitude": -73.9851,
        },
    )
    venue_id = venue_response.json()["id"]

    # Create reservation
    reservation_time = (datetime.utcnow() + timedelta(hours=2)).isoformat()
    client.post(
        "/reservations",
        json={
            "venue_id": venue_id,
            "time": reservation_time,
            "participant_user_ids": [user_id],
        },
    )

    # Get user reservations
    response = client.get(f"/reservations/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
