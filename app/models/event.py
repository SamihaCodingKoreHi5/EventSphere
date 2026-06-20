from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from app.database.base_class import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    date_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    
    organizer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )

    # Relationships
    organizer: Mapped["User"] = relationship("User", back_populates="events")
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="events")
    rsvps: Mapped[List["RSVP"]] = relationship(
        "RSVP", 
        back_populates="event", 
        cascade="all, delete-orphan"
    )
