from datetime import datetime

from src import local_db, session_store

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

        session_store.save_session(self.token, self.current_user)

        return {"ok":True, "user": result["user"]} 


    def logout(self) -> dict:
        self.token = None
        self.current_user = None
        session_store.clear_session()
        return {"ok":True}

    def get_current_user(self) -> dict | None:
        return self.current_user

    def restore_session(self) -> bool:
        session = session_store.load_session()

        if not session:
            return False

        self.token = session.get("token")
        self.current_user = session.get("user")

        return bool(self.token and self.current_user)

    

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

        return {
            "ok":True,
            "user_event_id": user_event_id,
            "time_in":now.isoformat()
        }

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

    def get_today(self) -> dict:
        if not self.token:
            return {
                "ok":False,
                "error":"Not Logged in"
            }
        return self.http.get_dtr_today(self.token)
       
        

    def get_status(self) -> dict:
        return {
            "pending": local_db.count_by_status("PENDING"),
            "synced": local_db.count_by_status("SYNCED")
        }