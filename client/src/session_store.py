import json

from pathlib import Path

session_file = Path.home() / ".dalia" / "session.json"


def save_session(token:str, user:dict) -> None:
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(
        json.dumps({"token":token, "user":user}),
        encoding="utf-8",
    )

def load_session() -> dict | None:
    if not session_file.exists():
        return None

    try:
        return json.loads(session_file.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return None


def clear_session() -> None:
    if session_file.exists():
        session_file.unlink()



