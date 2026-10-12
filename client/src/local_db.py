import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

db_path = Path.home() / ".dalia" / "local.db"

def _connect() -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db()->None:
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS local_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_event_id TEXT NOT NULL UNIQUE,
                user_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                error TEXT,
                retry_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_local_events_status on local_events(status);
""")


def enqueue_event(
    user_id: int,
    event_type: str,
    payload: dict
) -> str:

    user_event_id = str(uuid.uuid4())

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO local_events (user_event_id, user_id, event_type, payload, created_at)
            VALUES (?,?,?,?,?)
            """,

            (
                user_event_id,
                user_id,
                event_type,
                json.dumps(payload),
                datetime.now(timezone.utc).isoformat(),
            )

        )

    return user_event_id


def get_pending_events()-> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM local_events WHERE status = 'PENDING' ORDER BY id ASC"
        ).fetchall()

    return [dict(r) for r in rows]


def mark_synced(user_event_id: str) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE local_events SET status = 'SYNCED' WHERE user_event_id = ?",
            (user_event_id,)
        )



def mark_failed(user_event_id:str, error:str):

    with _connect() as conn:
        conn.execute(
            """
            UPDATE local_events
            SET ERROR = ?, retry_count = retry_count + 1
            WHERE user_event_id = ? 
            """,
            (error, user_event_id)
        )


def count_by_status(status:str) -> int:
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as n FROM local_events WHERE status = ?",
            (status,)
        ).fetchone()
    return row["n"]