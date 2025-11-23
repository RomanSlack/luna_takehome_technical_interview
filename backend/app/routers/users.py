from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models import User as UserModel, Friendship as FriendshipModel
from app.schemas import User, UserCreate, Friendship
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=User, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    db_user = UserModel(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    logger.info(f"Created user {db_user.id}", extra={"user_id": db_user.id})
    return db_user


@router.get("", response_model=List[User])
def list_users(db: Session = Depends(get_db)):
    """List all users."""
    users = db.query(UserModel).all()
    return users


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user."""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/friends", response_model=List[Friendship])
def get_user_friends(user_id: int, db: Session = Depends(get_db)):
    """Get a user's friends and friendship strengths."""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    friendships = db.query(FriendshipModel).filter(FriendshipModel.user_id == user_id).all()
    return friendships
