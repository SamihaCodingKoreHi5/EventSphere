import re
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.event import Event
from app.models.category import Category
from app.models.rsvp import RSVP
from app.schemas.event import EventCreate, EventUpdate
from app.schemas.category import CategoryCreate


def slugify(text: str) -> str:
    """Helper to convert names to URL-safe slugs."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text


class EventService:
    # --- Category Management ---
    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
        """Fetch category by ID."""
        return db.query(Category).filter(Category.id == category_id).first()

    @staticmethod
    def get_category_by_slug(db: Session, slug: str) -> Optional[Category]:
        """Fetch category by slug."""
        return db.query(Category).filter(Category.slug == slug).first()

    @staticmethod
    def get_all_categories(db: Session) -> List[Category]:
        """Get list of all categories."""
        return db.query(Category).all()

    @staticmethod
    def create_category(db: Session, category_in: CategoryCreate) -> Category:
        """Create category with slug validation/generation."""
        slug = category_in.slug or slugify(category_in.name)
        existing = EventService.get_category_by_slug(db, slug)
        if existing:
            return existing
            
        db_category = Category(
            name=category_in.name,
            slug=slug,
            description=category_in.description
        )
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    # --- Event Management ---
    @staticmethod
    def get_by_id(db: Session, event_id: int) -> Optional[Event]:
        """Fetch event by ID."""
        return db.query(Event).filter(Event.id == event_id).first()

    @staticmethod
    def get_all(
        db: Session,
        category_slug: Optional[str] = None,
        organizer_id: Optional[int] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """Fetch events with optional filters (category, organizer, search)."""
        query = db.query(Event)
        
        if category_slug:
            query = query.join(Category).filter(Category.slug == category_slug)
        if organizer_id:
            query = query.filter(Event.organizer_id == organizer_id)
        if search:
            query = query.filter(Event.title.ilike(f"%{search}%"))
            
        events = query.offset(skip).limit(limit).all()
        
        # Hydrate dynamic RSVP fields
        for event in events:
            EventService._hydrate_rsvp_fields(db, event)
            
        return events

    @staticmethod
    def create(db: Session, event_in: EventCreate, organizer_id: int) -> Event:
        """Create a new event."""
        db_event = Event(
            title=event_in.title,
            description=event_in.description,
            location=event_in.location,
            date_time=event_in.date_time,
            capacity=event_in.capacity,
            organizer_id=organizer_id,
            category_id=event_in.category_id
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return EventService._hydrate_rsvp_fields(db, db_event)

    @staticmethod
    def update(db: Session, db_event: Event, event_in: EventUpdate) -> Event:
        """Update an event."""
        update_data = event_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_event, field, value)
            
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return EventService._hydrate_rsvp_fields(db, db_event)

    @staticmethod
    def delete(db: Session, db_event: Event) -> None:
        """Delete an event."""
        db.delete(db_event)
        db.commit()

    @staticmethod
    def _hydrate_rsvp_fields(db: Session, event: Event) -> Event:
        """Helper to calculate and assign rsvp_count and spots_left."""
        rsvp_count = db.query(RSVP).filter(
            RSVP.event_id == event.id,
            RSVP.status == "confirmed"
        ).count()
        event.rsvp_count = rsvp_count
        event.spots_left = max(0, event.capacity - rsvp_count)
        return event
