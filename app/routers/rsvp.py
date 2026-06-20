from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.rsvp import RSVPCreate, RSVPResponse
from app.services.rsvp_service import RSVPService
from app.routers.deps import get_current_user

router = APIRouter()


@router.post("/", response_model=RSVPResponse, status_code=status.HTTP_201_CREATED)
def rsvp_to_event(
    rsvp_in: RSVPCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """RSVP to an event. Automatically sends email confirmation on success."""
    try:
        return RSVPService.create_rsvp(db, user=current_user, event_id=rsvp_in.event_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{event_id}", response_model=RSVPResponse)
def cancel_rsvp(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel RSVP for a specific event."""
    try:
        return RSVPService.cancel_rsvp(db, user_id=current_user.id, event_id=event_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=List[RSVPResponse])
def get_my_rsvps(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all RSVPs made by the authenticated user."""
    return RSVPService.get_user_rsvps(db, user_id=current_user.id)
