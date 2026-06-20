from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.database.base_class import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="User", nullable=False)  # User, Organizer, Admin
    
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
    events: Mapped[List["Event"]] = relationship(
        "Event", 
        back_populates="organizer", 
        cascade="all, delete-orphan"
    )
    rsvps: Mapped[List["RSVP"]] = relationship(
        "RSVP", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
