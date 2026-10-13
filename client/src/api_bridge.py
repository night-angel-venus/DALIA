from datetime import datetime

from src import local_db

class API:
    def __init__(self, http, worker=None):
        self.http = http
        self.worker = worker
        self.token = None
        self.current_user = None

    def login(self, email:str, password:str)->dict:
        result = self.http.login(email, password)

        if not result["ok"]:
            return result

        self.token = result["token"]

        self.current_user = result["user"]

        return {"ok":True, "user": result["user"]} 

    def is_logged_in(self) -> bool:
        return self.token is not None

    def time_in(self, shift_type:str) -> dict:
        if not self.current_user:
            return {"ok": False, "error":"Not logged in"}

        now = datetime.now()

        user_event_id = local_db.enqueue_event(
            user_id = self.current_user["id"],
            event_type="TIME_IN",
            payload={
                "shift_type": shift_type,
                "timestamp": now.isoformat(),
            }
        )

    def time_out(self) -> dict:
        if not self.current_user:
            return {"ok":False, "error": "Not logged in"}

        now = datetime.now()

        user_event_id = local_db.enqueue_event(
            user_id=self.current_user["id"],
            event_type="TIME_OUT",
            payload={"timestamp":now.isoformat()},
        )

        return {
            "ok":True,
            "user_event_id": user_event_id,
            "time_out":now.isoformat()
        }

    def get_status(self) -> dict:
        return {
            "pending": local_db.count_by_status("PENDING"),
            "synced": local_db.count_by_status("SYNCED")
        }