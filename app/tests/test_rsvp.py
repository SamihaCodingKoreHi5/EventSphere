from datetime import datetime, timedelta, timezone
from fastapi import status
from app.models.event import Event


def create_test_event(db, organizer_id, capacity=50) -> Event:
    event = Event(
        title="Test Event",
        location="Chicago",
        date_time=datetime.now(timezone.utc) + timedelta(days=2),
        capacity=capacity,
        organizer_id=organizer_id
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def test_rsvp_success(client, user_headers, db, test_organizer):
    """Test successful event RSVP."""
    event = create_test_event(db, test_organizer.id)
    
    response = client.post(
        "/api/v1/rsvp/",
        json={"event_id": event.id},
        headers=user_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["event_id"] == event.id
    assert data["status"] == "confirmed"


def test_rsvp_duplicate_prevention(client, user_headers, db, test_organizer):
    """Test user cannot RSVP to the same event twice."""
    event = create_test_event(db, test_organizer.id)
    
    # First RSVP -> Success
    client.post("/api/v1/rsvp/", json={"event_id": event.id}, headers=user_headers)
    
    # Second RSVP -> Bad Request
    response = client.post("/api/v1/rsvp/", json={"event_id": event.id}, headers=user_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already" in response.json()["detail"]


def test_rsvp_capacity_reached(client, user_headers, admin_headers, db, test_organizer):
    """Test RSVP fails if event capacity is full."""
    # Capacity is 1
    event = create_test_event(db, test_organizer.id, capacity=1)
    
    # Admin takes the only spot -> Success
    resp1 = client.post("/api/v1/rsvp/", json={"event_id": event.id}, headers=admin_headers)
    assert resp1.status_code == status.HTTP_201_CREATED

    # User tries to get a spot -> Fails
    resp2 = client.post("/api/v1/rsvp/", json={"event_id": event.id}, headers=user_headers)
    assert resp2.status_code == status.HTTP_400_BAD_REQUEST
    assert "booked" in resp2.json()["detail"]


def test_cancel_rsvp_success(client, user_headers, db, test_organizer):
    """Test successful RSVP cancellation."""
    event = create_test_event(db, test_organizer.id)
    
    # RSVP first
    client.post("/api/v1/rsvp/", json={"event_id": event.id}, headers=user_headers)
    
    # Cancel RSVP
    response = client.delete(f"/api/v1/rsvp/{event.id}", headers=user_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "cancelled"
