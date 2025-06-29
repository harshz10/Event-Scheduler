import pytest
import os
import json
from datetime import datetime, timedelta
from app import app, EVENTS_FILE

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Reset events file before each test
        with open(EVENTS_FILE, 'w') as f:
            json.dump([], f)
        yield client

def test_create_event(client):
    """Test creating a single event"""
    response = client.post('/events', json={
        "title": "Team Meeting",
        "description": "Weekly sync",
        "start_time": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=3)).isoformat(),
        "email": "team@example.com"
    })
    assert response.status_code == 201
    assert "id" in response.json[0]
    assert response.json[0]["title"] == "Team Meeting"

def test_create_recurring_event(client):
    """Test creating recurring events"""
    response = client.post('/events', json={
        "title": "Daily Yoga",
        "start_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=1.5)).isoformat(),
        "recurring": "1 day"
    })
    assert response.status_code == 201
    assert len(response.json) == 10  # Should create 10 occurrences

def test_get_events_sorted(client):
    """Test events are sorted earliest first"""
    # Create events in reverse order
    client.post('/events', json={
        "title": "Later Event",
        "start_time": (datetime.utcnow() + timedelta(hours=3)).isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=4)).isoformat()
    })
    client.post('/events', json={
        "title": "Earlier Event",
        "start_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=2)).isoformat()
    })
    
    response = client.get('/events')
    assert response.status_code == 200
    events = response.json
    assert events[0]["title"] == "Earlier Event"
    assert events[1]["title"] == "Later Event"

def test_update_event(client):
    """Test updating an event"""
    # Create event
    create_res = client.post('/events', json={
        "title": "Original Title",
        "start_time": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=3)).isoformat()
    })
    event_id = create_res.json[0]["id"]
    
    # Update event
    update_res = client.put(f'/events/{event_id}', json={
        "title": "Updated Title",
        "description": "New description"
    })
    assert update_res.status_code == 200
    assert update_res.json["title"] == "Updated Title"
    assert update_res.json["description"] == "New description"

def test_delete_event(client):
    """Test deleting an event"""
    # Create event
    create_res = client.post('/events', json={
        "title": "To Be Deleted",
        "start_time": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=3)).isoformat()
    })
    event_id = create_res.json[0]["id"]
    
    # Delete event
    delete_res = client.delete(f'/events/{event_id}')
    assert delete_res.status_code == 200
    
    # Verify deletion
    get_res = client.get('/events')
    assert len(get_res.json) == 0

def test_search_events(client):
    """Test event search functionality"""
    # Create test events
    client.post('/events', json={
        "title": "Important Meeting",
        "description": "Project discussion",
        "start_time": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=3)).isoformat()
    })
    client.post('/events', json={
        "title": "Lunch Break",
        "description": "Team lunch meeting",
        "start_time": (datetime.utcnow() + timedelta(hours=4)).isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=5)).isoformat()
    })
    
    # Search
    response = client.get('/events/search?q=meeting')
    assert response.status_code == 200
    assert len(response.json) == 2
    assert all("meeting" in event["title"].lower() or 
               "meeting" in event["description"].lower() 
               for event in response.json)

def test_invalid_event_creation(client):
    """Test validation for event creation"""
    # Missing title
    response = client.post('/events', json={
        "start_time": "2025-07-01T10:00:00+05:30",
        "end_time": "2025-07-01T11:00:00+05:30"
    })
    assert response.status_code == 400
    
    # Invalid time range
    response = client.post('/events', json={
        "title": "Invalid Time",
        "start_time": "2025-07-01T12:00:00+05:30",
        "end_time": "2025-07-01T11:00:00+05:30"
    })
    assert response.status_code == 400