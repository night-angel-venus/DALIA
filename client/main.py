import threading

import webview


from src import local_db
from src.api_bridge import API
from src.http_client import HttpClient
from src.sync_worker import SyncWorker


api_url = "http://127.0.0.1:8000/v1"
dev_mode = True


def main():
    local_db.init_db()

    http = HttpClient(api_url)

    api = API(http=http)

    worker = SyncWorker(http=http, get_token=lambda: api.token)

    api.worker = worker

    threading.Thread(target=worker.run, daemon=True).start()

    url = "http://localhost:5173" if dev_mode else "frontend/dist/index.html"

    webview.create_window("DALIA", url, js_api=api, width=700, height=1000)

    webview.start(debug=True)

if __name__ == "__main__":
    main()