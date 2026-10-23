import json
import requests


# This Client contains functions that simply
# Access the endpoints and pass data onto them

class HttpClient:
    def __init__(self, base_url:str, timeout:int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # Access to Login Endpoint (takes in 2 params)
    def login(self, email:str, password:str):

        #Actual Logic
        try:
            request = requests.post(
                f"{self.base_url}/login",
                data = {"username":email, "password":password},
                timeout=self.timeout
            )

        # Error Handlers
        except requests.RequestException as e:
            return {"ok": False, "error": str(e)}

        if request.status_code != 200:
            try:
                detail = request.json().get("detail", "Login failed")
            except ValueError:
                detail = "Login failed"
            return {"ok": False, "error":detail}


        # Parse data into JSON
        body = request.json()
        
        return {
            "ok":True,
            "token":body["access_token"],
            "user": body.get("user"),
        }

    # Gets the DTR of the day (1 param)
    def get_dtr_today(self, token:str):

        # Actual Logic
        try:
            request = requests.get(
                f"{self.base_url}/dtr/today",

                # headers contains the token
                headers={"Authorization":f"Bearer {token}"},
                timeout=self.timeout
                )


        # Error Handler   
        except requests.RequestException as e:
            return {"ok": False, "error": str(e)}

                
        if request.status_code == 200:
            return {"ok": True, "dtr": request.json()}
        
        return {"ok": False, "error": f"HTTP {request.status_code}: {request.text}"}

    # Acess to Sync Endpoint (2 params)
    def sync_event(self, token:str, event: dict):

        # payload comes from event, payload is essentially the DTR data
        payload = event["payload"]

        # If sqlite data says payload is a string,
        # parse it into JSON
        if isinstance(payload, str):
            payload = json.loads(payload)

        # Actual Sync Logic
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

        # Error Handler
        except requests.RequestException as e:
            return {"ok": False, "error": str(e)}

        if request.status_code in (200, 201):
            return {"ok": True, "body": request.json()}
        return {"ok": False, "error": f"HTTP {request.status_code}: {request.text}"}