from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserResponse


class RSVPBase(BaseModel):
    event_id: int


class RSVPCreate(RSVPBase):
    pass


class RSVPResponse(RSVPBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)
