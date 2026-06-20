from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.rsvp import RSVP
from app.models.event import Event
from app.models.user import User
from app.services.email import send_rsvp_confirmation
from app.services.event_service import EventService


class RSVPService:
    @staticmethod
    def get_rsvp(db: Session, user_id: int, event_id: int) -> Optional[RSVP]:
        """Fetch RSVP record for a user and event."""
        return db.query(RSVP).filter(
            RSVP.user_id == user_id,
            RSVP.event_id == event_id
        ).first()

    @staticmethod
    def create_rsvp(db: Session, user: User, event_id: int) -> RSVP:
        """
        Create a new RSVP or update a cancelled RSVP back to confirmed.
        Performs capacity checks, duplicate checks, and sends a confirmation email.
        """
        # Fetch event and calculate capacity
        event = EventService.get_by_id(db, event_id)
        if not event:
            raise ValueError("Event not found")

        # Refresh event to get current capacity stats
        EventService._hydrate_rsvp_fields(db, event)

        # Check if user already RSVP'd
        existing_rsvp = RSVPService.get_rsvp(db, user.id, event_id)
        
        if existing_rsvp:
            if existing_rsvp.status == "confirmed":
                raise ValueError("You have already RSVP'd to this event")
            else:
                # If they cancelled previously, re-confirm the RSVP
                if event.spots_left <= 0:
                    raise ValueError("This event is fully booked")
                existing_rsvp.status = "confirmed"
                db.add(existing_rsvp)
                db.commit()
                db.refresh(existing_rsvp)
                
                # Send email notification async/safely
                try:
                    send_rsvp_confirmation(
                        to_email=user.email,
                        user_name=user.full_name or user.email,
                        event_title=event.title,
                        event_date=event.date_time.strftime("%Y-%m-%d %H:%M UTC"),
                        event_location=event.location
                    )
                except Exception:
                    pass
                return existing_rsvp

        # Fresh RSVP
        if event.spots_left <= 0:
            raise ValueError("This event is fully booked")

        db_rsvp = RSVP(
            user_id=user.id,
            event_id=event_id,
            status="confirmed"
        )
        db.add(db_rsvp)
        db.commit()
        db.refresh(db_rsvp)

        # Send email notification
        try:
            send_rsvp_confirmation(
                to_email=user.email,
                user_name=user.full_name or user.email,
                event_title=event.title,
                event_date=event.date_time.strftime("%Y-%m-%d %H:%M UTC"),
                event_location=event.location
            )
        except Exception:
            pass

        return db_rsvp

    @staticmethod
    def cancel_rsvp(db: Session, user_id: int, event_id: int) -> RSVP:
        """Cancel an existing RSVP (change status to 'cancelled')."""
        rsvp = RSVPService.get_rsvp(db, user_id, event_id)
        if not rsvp:
            raise ValueError("RSVP not found")
        if rsvp.status == "cancelled":
            raise ValueError("RSVP is already cancelled")

        rsvp.status = "cancelled"
        db.add(rsvp)
        db.commit()
        db.refresh(rsvp)
        return rsvp

    @staticmethod
    def get_user_rsvps(db: Session, user_id: int) -> List[RSVP]:
        """Fetch all RSVPs for a given user."""
        return db.query(RSVP).filter(RSVP.user_id == user_id).all()
