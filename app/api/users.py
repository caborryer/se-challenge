from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
import logging

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.core.exceptions import UserNotFoundException, UserAlreadyExistsException

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user with the provided information. Username and email must be unique."
)
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise UserAlreadyExistsException(field="username", value=user.username)
    
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise UserAlreadyExistsException(field="email", value=user.email)
    
    db_user = User(**user.model_dump())
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        logger.error(f"Database integrity error creating user: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User creation failed due to data constraint violation"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating user"
        )


@router.get(
    "/",
    response_model=UserListResponse,
    summary="Get all users",
    description="Retrieve a paginated list of all users with optional filtering."
)
def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    active: bool = Query(None, description="Filter by active status"),
    role: str = Query(None, description="Filter by role"),
    db: Session = Depends(get_db)
) -> UserListResponse:
    query = db.query(User)
    
    if active is not None:
        query = query.filter(User.active == active)
    if role:
        query = query.filter(User.role == role)
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    return UserListResponse(
        total=total,
        users=users,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve a specific user by their unique identifier."
)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise UserNotFoundException(user_id=user_id)
    
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update an existing user's information. Only provided fields will be updated."
)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
) -> UserResponse:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise UserNotFoundException(user_id=user_id)
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "username" in update_data and update_data["username"] != db_user.username:
        existing = db.query(User).filter(User.username == update_data["username"]).first()
        if existing:
            raise UserAlreadyExistsException(field="username", value=update_data["username"])
    
    if "email" in update_data and update_data["email"] != db_user.email:
        existing = db.query(User).filter(User.email == update_data["email"]).first()
        if existing:
            raise UserAlreadyExistsException(field="email", value=update_data["email"])
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        logger.error(f"Database integrity error updating user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User update failed due to data constraint violation"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating user"
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user from the system permanently."
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise UserNotFoundException(user_id=user_id)
    
    try:
        db.delete(db_user)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deleting user"
        )

