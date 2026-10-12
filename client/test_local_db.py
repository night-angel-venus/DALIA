from src import local_db

local_db.init_db()

event_id = local_db.enqueue_event(
    user_id = 1,
    event_type = "TIME_IN",
    payload={
        "shift_type":"Full Day (8 Hours)",
        "timestamp":"2026-10-12T07:45:00"

    }
)
print(f"Enqueued: {event_id}")

pending = local_db.get_pending_events()

print(f"Pending after enqueue: {len(pending)}")
assert len(pending) == 1
assert pending[0]["user_event_id"] == event_id
assert pending[0]["status"] == "PENDING"

local_db.mark_synced(event_id)

pending = local_db.get_pending_events()
print(f"Pending after sync: {len(pending)}")
assert len(pending) == 0
print("All Good")