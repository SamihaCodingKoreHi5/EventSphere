from typing import Optional
from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    slug: Optional[str] = None  # Will be generated from name if not provided


class CategoryResponse(CategoryBase):
    id: int
    slug: str

    model_config = ConfigDict(from_attributes=True)
