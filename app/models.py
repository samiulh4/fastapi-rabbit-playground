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
    connection_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LogoutRequest(BaseModel):
    email: EmailStr

class ConnectionStore(BaseModel):
    user_id: str
    connection_id: str # Unique socket connection
    session_id: Optional[str] = None # Which chat room/session
    websocket_object_id: Optional[str] = None # For tracking actual WebSocket instance if needed
    status: str = "disconnected"
    client_ip: Optional[str] = None # Client/browser IP
    server_ip: Optional[str] = None # Server IP 
    user_agent: Optional[str] = None  # Browser/device information
    connected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    disconnected_at: Optional[datetime] = None      