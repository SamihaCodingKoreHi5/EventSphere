from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.database.base_class import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    events: Mapped[List["Event"]] = relationship(
        "Event", 
        back_populates="category"
    )
