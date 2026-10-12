from src import local_db
from src.http_client import HttpClient
from src.sync_worker import SyncWorker


API_URL = "http://127.0.0.1:8000/v1"


def main():
    local_db.init_db()
    local_db.clear_all()

    http = HttpClient(API_URL)

    result = http.login("yeon@bizsolvasia.com", "yeon")
    if not result["ok"]:
        print(f"Login failed: {result}")
        return
    token = result["token"]
    user_id = result["user"]["id"] if result["user"] else 1
    print(f"Logged in as user_id={user_id}")

    event_id = local_db.enqueue_event(
        user_id=user_id,
        event_type="TIME_IN",
        payload={
            "shift_type": "Full Day (8 Hours)",
            "timestamp": "2026-10-12T07:45:00",
        },
    )
    print(f"Enqueued {event_id}")

    worker = SyncWorker(http=http, get_token=lambda: token)
    count = worker.sync_once()
    print(f"Synced {count} event(s)")

    pending = local_db.get_pending_events()
    if len(pending) != 0:
        print(f"Still pending: {pending}")
        return
    print("Sync test passed.")


if __name__ == "__main__":
    main()