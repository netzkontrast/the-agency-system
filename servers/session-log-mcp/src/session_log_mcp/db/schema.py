"""Database schema management."""
from pathlib import Path
from typing import Optional
from . import get_conn

def ensure(path: Optional[Path] = None) -> None:
    """Ensure the schema is created and idempotent."""
    with get_conn(path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                ts TEXT NOT NULL,
                kind TEXT NOT NULL,
                spec_id TEXT,
                session_id TEXT,
                pr_number INTEGER,
                actor TEXT,
                payload TEXT NOT NULL,
                UNIQUE(session_id, ts, kind)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_spec_id ON events(spec_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_session_id ON events(session_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_kind_ts ON events(kind, ts)")
