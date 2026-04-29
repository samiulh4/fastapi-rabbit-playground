from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone

class User(BaseModel):
    name: str 
    email: EmailStr
    password: str
    mobile: Optional[str] = None
    gender: Optional[str] = None
    avatar: Optional[str] = None
    country: Optional[str] = Field(default=None, max_length=3)
    is_active: bool = False
    is_verified: bool = False
    is_online: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Message(BaseModel):
    sender_id: str
    content: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LogoutRequest(BaseModel):
    email: EmailStr  