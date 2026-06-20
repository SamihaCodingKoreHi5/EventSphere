from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Determine engine parameters (e.g. SQLite requires special connect arguments)
connect_args = {}
if settings.DATABASE_URL and settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create engine
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# Create SessionLocal factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI Dependency for database session lifecycle management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
