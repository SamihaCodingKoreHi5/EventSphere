from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.schemas.category import CategoryCreate, CategoryResponse
from app.services.event_service import EventService
from app.routers.deps import get_current_user, RoleChecker

router = APIRouter()


# --- Category Endpoints ---

@router.get("/categories", response_model=List[CategoryResponse])
def read_categories(db: Session = Depends(get_db)):
    """Fetch all event categories."""
    return EventService.get_all_categories(db)


@router.post(
    "/categories", 
    response_model=CategoryResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(["Organizer", "Admin"]))]
)
def create_category(category_in: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category (Organizer/Admin only)."""
    return EventService.create_category(db, category_in)


# --- Event Endpoints ---

@router.get("/", response_model=List[EventResponse])
def read_events(
    category: Optional[str] = None,
    organizer_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all events with optional filters (category slug, organizer, title search)."""
    return EventService.get_all(
        db, category_slug=category, organizer_id=organizer_id, search=search, skip=skip, limit=limit
    )


@router.get("/{event_id}", response_model=EventResponse)
def read_event(event_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a single event."""
    event = EventService.get_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return EventService._hydrate_rsvp_fields(db, event)


@router.post(
    "/", 
    response_model=EventResponse, 
    status_code=status.HTTP_201_CREATED
)
def create_event(
    event_in: EventCreate,
    current_user: User = Depends(RoleChecker(["Organizer", "Admin"])),
    db: Session = Depends(get_db)
):
    """Create a new event (Organizer/Admin only)."""
    # Verify category exists if provided
    if event_in.category_id:
        category = EventService.get_category_by_id(db, event_in.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )
            
    return EventService.create(db, event_in=event_in, organizer_id=current_user.id)


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_in: EventUpdate,
    current_user: User = Depends(RoleChecker(["Organizer", "Admin"])),
    db: Session = Depends(get_db)
):
    """Update event details (Event owner or Admin only)."""
    event = EventService.get_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
        
    # Verify ownership or admin role
    if event.organizer_id != current_user.id and current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this event"
        )
        
    # Verify category exists if changing category
    if event_in.category_id:
        category = EventService.get_category_by_id(db, event_in.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )

    return EventService.update(db, db_event=event, event_in=event_in)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    current_user: User = Depends(RoleChecker(["Organizer", "Admin"])),
    db: Session = Depends(get_db)
):
    """Delete an event (Event owner or Admin only)."""
    event = EventService.get_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
        
    # Verify ownership or admin role
    if event.organizer_id != current_user.id and current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this event"
        )
        
    EventService.delete(db, db_event=event)
    return None
