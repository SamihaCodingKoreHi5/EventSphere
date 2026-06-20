from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.user import User
from app.models.event import Event
from app.models.rsvp import RSVP
from app.schemas.user import UserResponse
from app.schemas.event import EventResponse
from app.services.user_service import UserService
from app.services.event_service import EventService
from app.routers.deps import RoleChecker

router = APIRouter(
    dependencies=[Depends(RoleChecker(["Admin"]))]
)


@router.get("/users", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Fetch all registered users on the platform (Admin only)."""
    return UserService.get_all(db, skip=skip, limit=limit)


@router.get("/events", response_model=List[EventResponse])
def get_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Fetch all events on the platform (Admin only)."""
    return EventService.get_all(db, skip=skip, limit=limit)


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def force_delete_event(event_id: int, db: Session = Depends(get_db)):
    """Force delete any event from the platform (Admin only)."""
    event = EventService.get_by_id(db, event_id)
    if event:
        EventService.delete(db, db_event=event)
    return None


@router.get("/stats", response_model=Dict[str, Any])
def get_platform_stats(db: Session = Depends(get_db)):
    """Retrieve administrative dashboard statistics (Admin only)."""
    # Counts
    total_users = db.query(User).count()
    total_events = db.query(Event).count()
    total_rsvps = db.query(RSVP).count()
    confirmed_rsvps = db.query(RSVP).filter(RSVP.status == "confirmed").count()
    
    # Roles breakdown
    roles = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    roles_breakdown = {role: count for role, count in roles}
    
    # Popular event (event with most confirmed RSVPs)
    popular_event_data = db.query(
        RSVP.event_id, 
        func.count(RSVP.id).label("cnt")
    ).filter(RSVP.status == "confirmed").group_by(RSVP.event_id).order_type = "cnt"
    
    popular_event = db.query(
        RSVP.event_id, 
        func.count(RSVP.id).label("cnt")
    ).filter(RSVP.status == "confirmed").group_by(RSVP.event_id).order_by(func.count(RSVP.id).desc()).first()
    
    popular_event_details = None
    if popular_event:
        event = EventService.get_by_id(db, popular_event.event_id)
        if event:
            popular_event_details = {
                "id": event.id,
                "title": event.title,
                "rsvp_count": popular_event.cnt
            }

    return {
        "total_users": total_users,
        "total_events": total_events,
        "total_rsvps": total_rsvps,
        "confirmed_rsvps": confirmed_rsvps,
        "roles_breakdown": roles_breakdown,
        "popular_event": popular_event_details
    }
