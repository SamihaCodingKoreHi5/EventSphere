# Import all the models, so that Base has them before being
# imported by Alembic or database setup scripts.
from app.database.base_class import Base
from app.models.user import User
from app.models.category import Category
from app.models.event import Event
from app.models.rsvp import RSVP
