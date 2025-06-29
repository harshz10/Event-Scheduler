import os
import json
import threading
import time
import re
from datetime import datetime, timedelta
from flask import Flask, jsonify, request

app = Flask(__name__)
EVENTS_FILE = "events.json"
lock = threading.Lock()

# Create events file if doesn't exist
if not os.path.exists(EVENTS_FILE):
    with open(EVENTS_FILE, "w") as f:
        json.dump([], f)

def load_events():
    with lock:
        with open(EVENTS_FILE, "r") as f:
            return json.load(f)

def save_events(events):
    with lock:
        with open(EVENTS_FILE, "w") as f:
            json.dump(events, f, indent=2)

def parse_recurrence(recur_str, base_date):
    """Parse recurrence pattern into datetime objects"""
    if not recur_str:
        return [base_date]
    
    pattern = r'(\d+)\s*(day|week|month)'
    match = re.match(pattern, recur_str.lower())
    if not match:
        return [base_date]
    
    num = int(match.group(1))
    unit = match.group(2)
    
    occurrences = []
    for i in range(10):  # Generate 10 occurrences
        if unit == "day":
            new_date = base_date + timedelta(days=num*i)
        elif unit == "week":
            new_date = base_date + timedelta(weeks=num*i)
        elif unit == "month":
            # Simple month addition
            year = base_date.year + (base_date.month + num*i - 1) // 12
            month = (base_date.month + num*i - 1) % 12 + 1
            day = min(base_date.day, [31,29 if year%4==0 else 28,31,30,31,30,31,31,30,31,30,31][month-1])
            new_date = datetime(year, month, day, base_date.hour, base_date.minute)
        occurrences.append(new_date)
    
    return occurrences

def check_reminders():
    while True:
        now = datetime.utcnow()
        events = load_events()
        
        for event in events:
            start_time = datetime.fromisoformat(event["start_time"])
            time_diff = start_time - now
            
            if timedelta(0) <= time_diff <= timedelta(hours=1):
                print(f"\nREMINDER: Event '{event['title']}' starting soon!")
                print(f"Time: {start_time.strftime('%Y-%m-%d %H:%M')}")
                print(f"Description: {event['description']}\n")
                
                # Email notification if configured
                if event.get("email") and "@" in event["email"]:
                    # In a real app, you'd send an actual email here
                    print(f"Email sent to {event['email']} about '{event['title']}'")
        
        time.sleep(60)

# Start reminder thread
reminder_thread = threading.Thread(target=check_reminders, daemon=True)
reminder_thread.start()

@app.route("/events", methods=["POST"])
def create_event():
    data = request.get_json()
    
    if not all(key in data for key in ("title", "start_time", "end_time")):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        start = datetime.fromisoformat(data["start_time"])
        end = datetime.fromisoformat(data["end_time"])
        if start >= end:
            return jsonify({"error": "End time must be after start time"}), 400
    except ValueError:
        return jsonify({"error": "Invalid time format. Use ISO format"}), 400
    
    events = load_events()
    event_id = max([e["id"] for e in events], default=0) + 1
    
    # Handle recurring events
    recurrences = parse_recurrence(data.get("recurring"), start)
    created_events = []
    
    for i, occurrence in enumerate(recurrences):
        duration = end - start
        new_end = occurrence + duration
        
        new_event = {
            "id": event_id + i,
            "title": data["title"],
            "description": data.get("description", ""),
            "start_time": occurrence.isoformat(),
            "end_time": new_end.isoformat(),
            "email": data.get("email", ""),
            "recurring": data.get("recurring", "")
        }
        created_events.append(new_event)
        events.append(new_event)
    
    save_events(events)
    return jsonify(created_events), 201

@app.route("/events", methods=["GET"])
def get_events():
    events = load_events()
    sorted_events = sorted(
        events, 
        key=lambda x: datetime.fromisoformat(x["start_time"])
    )
    return jsonify(sorted_events)

@app.route("/events/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    data = request.get_json()
    events = load_events()
    
    for event in events:
        if event["id"] == event_id:
            if "start_time" in data or "end_time" in data:
                start = datetime.fromisoformat(data.get("start_time", event["start_time"]))
                end = datetime.fromisoformat(data.get("end_time", event["end_time"]))
                if start >= end:
                    return jsonify({"error": "End time must be after start time"}), 400
            
            event.update({
                "title": data.get("title", event["title"]),
                "description": data.get("description", event["description"]),
                "start_time": data.get("start_time", event["start_time"]),
                "end_time": data.get("end_time", event["end_time"]),
                "email": data.get("email", event.get("email", "")),
                "recurring": data.get("recurring", event.get("recurring", ""))
            })
            
            save_events(events)
            return jsonify(event)
    
    return jsonify({"error": "Event not found"}), 404

@app.route("/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    events = load_events()
    new_events = [e for e in events if e["id"] != event_id]
    
    if len(events) == len(new_events):
        return jsonify({"error": "Event not found"}), 404
    
    save_events(new_events)
    return jsonify({"message": "Event deleted"}), 200

@app.route("/events/search", methods=["GET"])
def search_events():
    query = request.args.get("q", "").lower()
    if not query:
        return jsonify({"error": "Missing search query"}), 400
    
    events = load_events()
    results = [
        e for e in events
        if query in e["title"].lower() or query in e["description"].lower()
    ]
    
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)