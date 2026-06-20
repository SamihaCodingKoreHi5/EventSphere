from fastapi import status
from datetime import datetime, timedelta, timezone
from app.models.event import Event


def test_admin_get_users_list(client, admin_headers, user_headers, test_organizer):
    """Test admin can view all users, but regular user cannot."""
    # Regular user -> Forbidden
    response = client.get("/api/v1/admin/users", headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Admin -> Success
    response = client.get("/api/v1/admin/users", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 3  # Admin, Organizer, User from conftest



def test_admin_delete_event(client, admin_headers, db, test_organizer):
    """Test admin can delete any event regardless of owner."""
    event = Event(
        title="Admin Mod Event",
        location="Miami",
        date_time=datetime.now(timezone.utc) + timedelta(days=1),
        capacity=100,
        organizer_id=test_organizer.id
    )
    db.add(event)
    db.commit()

    # Admin delete -> Success
    response = client.delete(f"/api/v1/admin/events/{event.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Confirm deletion
    assert db.query(Event).filter_by(id=event.id).first() is None


def test_admin_get_stats(client, admin_headers, db, test_organizer, test_user):
    """Test administrative dashboard statistics endpoint."""
    event = Event(
        title="Miami conference",
        location="Miami",
        date_time=datetime.now(timezone.utc) + timedelta(days=1),
        capacity=100,
        organizer_id=test_organizer.id
    )
    db.add(event)
    db.commit()

    response = client.get("/api/v1/admin/stats", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_users"] == 3
    assert data["total_events"] == 1
    assert data["total_rsvps"] == 0
