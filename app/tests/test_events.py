from datetime import datetime, timedelta, timezone
from fastapi import status
from app.models.category import Category


def test_create_category(client, organizer_headers):
    """Test category creation by organizer/admin."""
    response = client.post(
        "/api/v1/events/categories",
        json={"name": "Business Development", "description": "Business workshops"},
        headers=organizer_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Business Development"
    assert data["slug"] == "business-development"


def test_create_category_forbidden_for_user(client, user_headers):
    """Test regular users cannot create categories."""
    response = client.post(
        "/api/v1/events/categories",
        json={"name": "Gaming", "description": "Gaming tournaments"},
        headers=user_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_event_success(client, organizer_headers, db):
    """Test organizer successfully creates an event."""
    category = db.query(Category).filter_by(slug="technology").first()
    future_date = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    
    response = client.post(
        "/api/v1/events/",
        json={
            "title": "Python Hackathon",
            "description": "FastAPI hacking",
            "location": "Online",
            "date_time": future_date,
            "capacity": 20,
            "category_id": category.id
        },
        headers=organizer_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Python Hackathon"
    assert data["capacity"] == 20
    assert data["rsvp_count"] == 0
    assert data["spots_left"] == 20


def test_create_event_unauthorized_role(client, user_headers):
    """Test regular users cannot create events."""
    future_date = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    response = client.post(
        "/api/v1/events/",
        json={
            "title": "Hackathon",
            "location": "Online",
            "date_time": future_date,
            "capacity": 10
        },
        headers=user_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_read_events_list(client, db, test_organizer):
    """Test listing public events."""
    from app.models.event import Event
    event = Event(
        title="Event 1",
        location="NY",
        date_time=datetime.now(timezone.utc) + timedelta(days=5),
        capacity=100,
        organizer_id=test_organizer.id
    )
    db.add(event)
    db.commit()

    response = client.get("/api/v1/events/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1


def test_update_event_ownership(client, organizer_headers, user_headers, db, test_organizer):
    """Test owner can update event but other organizer/user cannot."""
    from app.models.event import Event
    event = Event(
        title="Editable Event",
        location="LA",
        date_time=datetime.now(timezone.utc) + timedelta(days=1),
        capacity=50,
        organizer_id=test_organizer.id
    )
    db.add(event)
    db.commit()

    # User try edit -> Forbidden
    resp = client.put(
        f"/api/v1/events/{event.id}",
        json={"title": "Updated by Hackers"},
        headers=user_headers
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Owner try edit -> Success
    resp = client.put(
        f"/api/v1/events/{event.id}",
        json={"title": "Updated by Owner"},
        headers=organizer_headers
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["title"] == "Updated by Owner"
