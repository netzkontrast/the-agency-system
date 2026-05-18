import json
from unittest.mock import patch
from session_log_mcp.tools.record import record_event
from session_log_mcp.db import get_conn

def test_record_idempotency(tmp_path):
    db_path = tmp_path / "test.db"

    # We patch get_conn to always return a connection to our tmp db
    def mock_get_conn(path=None):
        return get_conn(db_path)

    with patch("session_log_mcp.db.schema.get_conn", side_effect=mock_get_conn), \
         patch("session_log_mcp.tools.record.get_conn", side_effect=mock_get_conn):

        from session_log_mcp.db.schema import ensure
        ensure(db_path)

        # First call
        res1 = json.loads(record_event(
            kind="test",
            payload={"foo": "bar"},
            session_id="session-1",
            ts="2023-01-01T00:00:00Z"
        ))

        assert res1["inserted"] is True
        assert res1["id"] is not None

        # Second call
        res2 = json.loads(record_event(
            kind="test",
            payload={"foo": "bar"},
            session_id="session-1",
            ts="2023-01-01T00:00:00Z"
        ))

        assert res2["inserted"] is False
        assert res2["id"] == res1["id"]

        # Verify 1 row
        with get_conn(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as c FROM events")
            assert cursor.fetchone()["c"] == 1
