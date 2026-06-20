from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.user import UserResponse
from app.schemas.category import CategoryResponse


class EventBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    location: str = Field(..., min_length=2, max_length=255)
    date_time: datetime
    capacity: int = Field(..., gt=0)
    category_id: Optional[int] = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = Field(None, min_length=2, max_length=255)
    date_time: Optional[datetime] = None
    capacity: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = None


class EventResponse(EventBase):
    id: int
    organizer_id: int
    created_at: datetime
    updated_at: datetime
    
    # Nested schemas
    organizer: UserResponse
    category: Optional[CategoryResponse] = None
    
    # Dynamically calculated fields
    rsvp_count: int = 0
    spots_left: int = 0

    model_config = ConfigDict(from_attributes=True)
