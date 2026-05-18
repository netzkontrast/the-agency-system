"""Database connection helper."""
import sqlite3
from pathlib import Path
from typing import Optional

def get_conn(path: Optional[Path] = None) -> sqlite3.Connection:
    if path is None:
        path = Path.home() / ".agency-system" / "session-log" / "log.db"

    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn
