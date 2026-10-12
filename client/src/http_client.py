import json
import requests


class HttpClient:
    def __init__(self, base_url:str, timeout:int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def login(self, email:str, password:str):
        try:
            request = requests.post(
                f"{self.base_url}/login",
                data = {"username":email, "password":password},
                timeout=self.timeout
            )

        except requests.RequestException as e:
            return {"ok": False, "error": str(e)}

        if request.status_code != 200:
            try:
                detail = request.json().get("detail", "Login failed")
            except ValueError:
                detail = "Login failed"
            return {"ok": False, "error":detail}


        body = request.json()
        
        return {
            "ok":True,
            "token":body["access_token"],
            "user": body.get("user"),
        }

    def sync_event(self, token:str, event: dict):
        payload = event["payload"]

        if isinstance(payload, str):
            payload = json.loads(payload)

        try:
            request =  requests.post(
                f"{self.base_url}/dtr/sync",
                json={
                    "user_event_id": event["user_event_id"],
                    "user_id": event["user_id"],
                    "event_type": event["event_type"],
                    "payload": payload,
                    "created_at": event["created_at"],
                },
                headers={"Authorization":f"Bearer {token}"},
                timeout=self.timeout
            )
        except requests.RequestException as e:
            return {"ok": False, "error": str(e)}

        if request.status_code in (200, 201):
            return {"ok": True, "body": request.json()}
        return {"ok": False, "error": f"HTTP {request.status_code}: {request.text}"}