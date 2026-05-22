import json
import time
from unittest.mock import patch
from session_log_mcp.tools.record import record_event
from session_log_mcp.tools.summary import summary_events
from session_log_mcp.db import get_conn

def test_summary_performance_and_correctness(tmp_path):
    db_path = tmp_path / "test.db"

    def mock_get_conn(path=None):
        return get_conn(db_path)

    with patch("session_log_mcp.db.schema.get_conn", side_effect=mock_get_conn), \
         patch("session_log_mcp.tools.record.get_conn", side_effect=mock_get_conn), \
         patch("session_log_mcp.tools.summary.get_conn", side_effect=mock_get_conn):

        from session_log_mcp.db.schema import ensure
        ensure(db_path)

        # Insert 10k rows
        # For testing we'll do bulk insert instead of individual calls to avoid test timeouts
        with get_conn(db_path) as conn:
            cursor = conn.cursor()
            kinds = ["k1", "k2", "k3", "k4", "k5"]
            rows = []
            for i in range(10000):
                kind = kinds[i % 5]
                # Avoid UNIQUE constraint violation by adding seconds/ms
                ts = f"2023-01-01T{i%24:02d}:00:{i%60:02d}.{i:04d}Z"
                rows.append((ts, kind, "050", f"session-{i//1000}", i, "actor", "{}"))
            cursor.executemany("""
                INSERT INTO events (ts, kind, spec_id, session_id, pr_number, actor, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, rows)
            conn.commit()

        # Test summary
        start_time = time.time()
        res = json.loads(summary_events(spec_id="050"))
        duration = time.time() - start_time

        assert duration < 0.2, f"Summary took {duration}s, should be < 0.2s"
        assert res["total"] == 10000
        assert len(res["counts_by_kind"]) == 5
        assert res["counts_by_kind"]["k1"] == 2000
        assert res["latest_event"] is not None
        assert res["latest_event"]["spec_id"] == "050"
