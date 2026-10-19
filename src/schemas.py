import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# -------------------------------------------------------------
# User Schemas
# -------------------------------------------------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, description="Password must be at least 6 characters")
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# -------------------------------------------------------------
# Book Schemas (CRUD)
# -------------------------------------------------------------
class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    publisher: Optional[str] = ""
    published_date: Optional[str] = ""
    page_count: Optional[int] = Field(default=0, ge=0)
    language: Optional[str] = "English"


class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    author: Optional[str] = Field(default=None, min_length=1, max_length=255)
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    page_count: Optional[int] = Field(default=None, ge=0)
    language: Optional[str] = None


class BookResponse(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    publisher: Optional[str] = ""
    published_date: Optional[str] = ""
    page_count: int = 0
    language: str = "English"
    created_at: datetime
    user_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)
