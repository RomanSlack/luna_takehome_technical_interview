from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.models import InterestStatus, ReservationStatus, ParticipantStatus


class UserBase(BaseModel):
    name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class VenueBase(BaseModel):
    name: str
    category: str
    address: str
    latitude: float
    longitude: float
    description: Optional[str] = None


class VenueCreate(VenueBase):
    pass


class Venue(VenueBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UserInterestBase(BaseModel):
    venue_id: int
    status: InterestStatus


class UserInterestCreate(UserInterestBase):
    pass


class UserInterest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    venue_id: int
    status: InterestStatus
    created_at: datetime


class Friendship(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    friend_id: int
    strength: float
    friend: User


class RecommendedPerson(BaseModel):
    user: User
    compatibility_score: float


class RecommendedVenue(BaseModel):
    venue: Venue
    score: float
    recommended_people: List[RecommendedPerson]


class RecommendationsResponse(BaseModel):
    recommended_venues: List[RecommendedVenue]


class ReservationCreate(BaseModel):
    venue_id: int
    time: datetime
    participant_user_ids: List[int]


class ReservationAccept(BaseModel):
    reservation_id: int
    user_id: int


class ReservationParticipant(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: ParticipantStatus
    user: User


class Reservation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    venue_id: int
    created_by_user_id: int
    time: datetime
    status: ReservationStatus
    created_at: datetime
    venue: Venue
    participants: List[ReservationParticipant]


class AgentResult(BaseModel):
    success: bool
    message: str
    reservation: Optional[Reservation] = None
