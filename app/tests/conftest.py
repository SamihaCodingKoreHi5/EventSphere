import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.base_class import Base
from app.database.session import get_db
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.category import Category

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """Create a fresh database session for a test function."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Seed base categories
    tech = Category(name="Technology", slug="technology", description="Tech events")
    music = Category(name="Music", slug="music", description="Music events")
    session.add_all([tech, music])
    session.commit()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def get_auth_headers(email: str) -> dict:
    """Generate mock JWT authentication headers."""
    token = create_access_token(subject=email)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_admin(db) -> User:
    """Fixture to create and return an Admin user."""
    admin = User(
        email="admin@test.com",
        hashed_password=get_password_hash("password"),
        full_name="Admin Test",
        role="Admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def test_organizer(db) -> User:
    """Fixture to create and return an Organizer user."""
    organizer = User(
        email="organizer@test.com",
        hashed_password=get_password_hash("password"),
        full_name="Organizer Test",
        role="Organizer"
    )
    db.add(organizer)
    db.commit()
    db.refresh(organizer)
    return organizer


@pytest.fixture
def test_user(db) -> User:
    """Fixture to create and return a regular User."""
    user = User(
        email="user@test.com",
        hashed_password=get_password_hash("password"),
        full_name="User Test",
        role="User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_headers(test_admin) -> dict:
    return get_auth_headers(test_admin.email)


@pytest.fixture
def organizer_headers(test_organizer) -> dict:
    return get_auth_headers(test_organizer.email)


@pytest.fixture
def user_headers(test_user) -> dict:
    return get_auth_headers(test_user.email)
