from app.routers.auth import router as auth_router
from app.routers.events import router as events_router
from app.routers.rsvp import router as rsvp_router
from app.routers.admin import router as admin_router

__all__ = ["auth_router", "events_router", "rsvp_router", "admin_router"]
