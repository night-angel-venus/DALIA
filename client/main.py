import threading

import webview

import os
import sys

from src import local_db
from src.api_bridge import API
from src.http_client import HttpClient
from src.sync_worker import SyncWorker


api_url = "http://192.168.1.100:8000/v1"
dev_mode = False


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    local_db.init_db()

    http = HttpClient(api_url)

    api = API(http=http)

    if api.restore_session():
        print("[SYSTEM] Saved session restored.")
    else:
        print("[SYSTEM] No Saved Session, Please Log In")


    worker = SyncWorker(http=http, get_token=lambda: api.token)

    api.worker = worker

    threading.Thread(target=worker.run, daemon=True).start()

    if dev_mode:
        url = "http://127.0.0.1:5173"
    else:
        url = resource_path(os.path.join("frontend", "dist", "index.html"))


    url = "http://127.0.0.1:5173" if dev_mode else "frontend/dist/index.html"

    webview.create_window("DALIA", url, js_api=api, width=400, height=600, resizable=False)

    webview.start(debug=dev_mode, private_mode=True)

if __name__ == "__main__":
    main()