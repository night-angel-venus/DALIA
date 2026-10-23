import threading

from src import local_db

# This file is responsible for syncing the sqlite data to the DB

class SyncWorker:
    def __init__(self, http, get_token, interval_seconds: int = 30):
        self.http=http
        self.get_token=get_token
        self.interval=interval_seconds
        self._stop = threading.Event()

    def sync_once(self) -> int:
        token = self.get_token()

        if not token:
            return 0

        synced = 0

        for event in local_db.get_pending_events():
            result = self.http.sync_event(token, event)

            if result["ok"]:
                local_db.mark_synced(event["user_event_id"])
                synced += 1
            else:
                local_db.mark_failed(event["user_event_id"], result["error"])

        return synced

    def run(self) -> None:
        while not self._stop.is_set():
            try:
                self.sync_once()
            except Exception as e:
                print(f"[sync] unexpected error: {e}")
            self._stop.wait(self.interval)

    def stop(self)->None:
        self._stop.set()