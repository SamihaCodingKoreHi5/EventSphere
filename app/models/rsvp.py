from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base_class import Base


class RSVP(Base):
    __tablename__ = "rsvps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), 
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), 
        default="confirmed", 
        nullable=False
    )  # confirmed, cancelled
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="rsvps")
    event: Mapped["Event"] = relationship("Event", back_populates="rsvps")

    # Composite Unique Constraint to prevent duplicate RSVPs
    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_event_rsvp"),
    )
