from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = "User"  # User, Organizer, Admin


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    email: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
