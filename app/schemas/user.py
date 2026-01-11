from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User's email address")
    first_name: str = Field(..., min_length=1, max_length=50, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="User's last name")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    active: bool = Field(default=True, description="Whether the user is active")
    
    @validator("username")
    def username_alphanumeric(cls, v):
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        return v
    
    @validator("first_name", "last_name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty or only whitespace")
        return v.strip()


class UserCreate(UserBase):
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "user",
                "active": True
            }
        }


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    role: Optional[UserRole] = None
    active: Optional[bool] = None
    
    @validator("username")
    def username_alphanumeric(cls, v):
        if v is not None and not v.replace("_", "").isalnum():
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        return v
    
    @validator("first_name", "last_name")
    def name_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty or only whitespace")
        return v.strip() if v else v
    
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Jane",
                "email": "jane.doe@example.com",
                "active": False
            }
        }


class UserResponse(UserBase):
    id: int = Field(..., description="Unique user identifier")
    created_at: datetime = Field(..., description="Timestamp when user was created")
    updated_at: datetime = Field(..., description="Timestamp when user was last updated")
    
    class Config:
        from_attributes = True  # Allows creation from ORM models
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "user",
                "active": True,
                "created_at": "2024-01-10T10:00:00Z",
                "updated_at": "2024-01-10T10:00:00Z"
            }
        }


class UserListResponse(BaseModel):
    total: int = Field(..., description="Total number of users")
    users: List[UserResponse] = Field(..., description="List of users")
    skip: int = Field(default=0, description="Number of records skipped")
    limit: int = Field(default=100, description="Maximum number of records returned")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "users": [
                    {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john.doe@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "role": "user",
                        "active": True,
                        "created_at": "2024-01-10T10:00:00Z",
                        "updated_at": "2024-01-10T10:00:00Z"
                    }
                ],
                "skip": 0,
                "limit": 10
            }
        }

