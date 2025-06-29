# Event Scheduler System 

```markdown
# Event Scheduler System

## Overview
This is a RESTful API for managing events with reminders. The application allows users to create, view, update, and delete events with persistent storage.

## Installation
### Prerequisites
- Python 3.8+
- pip package manager

### Steps
1. Clone the repository:
```bash
git clone https://github.com/harshz10/event-scheduler.git
cd event-scheduler
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application
Start the server:
```bash
python app.py
```

The application will be available at:
```
http://localhost:5000
```

## Example Usage
### 1. Create an Event
```bash
curl -X POST http://localhost:5000/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Meeting",
    "description": "Weekly sync",
    "start_time": "2025-07-01T10:00:00+05:30",
    "end_time": "2025-07-01T11:00:00+05:30",
    "email": "team@example.com"
  }'
```

**Output:**
```json
{
  "id": 1,
  "title": "Team Meeting",
  "description": "Weekly sync",
  "start_time": "2025-07-01T10:00:00+05:30",
  "end_time": "2025-07-01T11:00:00+05:30",
  "email": "team@example.com"
}
```

### 2. Create a Recurring Event
```bash
curl -X POST http://localhost:5000/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Morning Yoga",
    "description": "Daily session",
    "start_time": "2025-07-02T06:30:00+05:30",
    "end_time": "2025-07-02T07:00:00+05:30",
    "recurring": "1 day"
  }'
```

**Output:**
```json
{
  "id": 2,
  "title": "Morning Yoga",
  "description": "Daily session",
  "start_time": "2025-07-02T06:30:00+05:30",
  "end_time": "2025-07-02T07:00:00+05:30",
  "recurring": "1 day"
}
```

### 3. List All Events
```bash
curl http://localhost:5000/events
```

**Output:**
```json
[
  {
    "id": 2,
    "title": "Morning Yoga",
    "description": "Daily session",
    "start_time": "2025-07-02T06:30:00+05:30",
    "end_time": "2025-07-02T07:00:00+05:30",
    "recurring": "1 day"
  },
  {
    "id": 1,
    "title": "Team Meeting",
    "description": "Weekly sync",
    "start_time": "2025-07-01T10:00:00+05:30",
    "end_time": "2025-07-01T11:00:00+05:30",
    "email": "team@example.com"
  }
]
```

### 4. Update an Event
```bash
curl -X PUT http://localhost:5000/events/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Meeting",
    "description": "New agenda"
  }'
```

**Output:**
```json
{
  "id": 1,
  "title": "Updated Meeting",
  "description": "New agenda",
  "start_time": "2025-07-01T10:00:00+05:30",
  "end_time": "2025-07-01T11:00:00+05:30",
  "email": "team@example.com"
}
```

### 5. Delete an Event
```bash
curl -X DELETE http://localhost:5000/events/1
```

**Output:**
```json
{
  "message": "Event deleted"
}
```

### 6. Search Events
```bash
curl http://localhost:5000/events/search?q=meeting
```

**Output:**
```json
[
    {
        "description": "Weekly sync",
        "email": "team@example.com",
        "end_time": "2025-07-01T11:00:00+05:30",
        "id": 1,
        "recurring": "1 week",
        "start_time": "2025-07-01T10:00:00+05:30",
        "title": "Team Meeting"
    },
    {
        "description": "Meeting with the class teacher to discuss academic performance.",
        "email": "parents@example.com",
        "end_time": "2025-07-06T09:00:00+05:30",
        "id": 4,
        "recurring": "none",
        "start_time": "2025-07-06T08:30:00+05:30",
        "title": "Parent-Teacher Meeting"
    }
]
```

## Reminder System
The application automatically checks for upcoming events every minute. Events starting within the next hour will trigger:

1. Console notifications:
```
REMINDER: Event 'Morning Yoga' starting soon!
Time: 2025-07-02 06:30
Description: Daily session
```

2. Email notifications (if email is provided):
```
Email sent to team@example.com
```

## Postman Collection
A Postman collection is included in the repository (`EventScheduler.postman_collection.json`) with pre-configured requests for all API endpoints.

## Testing
To run unit tests:
```bash
pytest test_app.py
```
