import json
from unittest.mock import patch
from session_log_mcp.tools.record import record_event
from session_log_mcp.tools.query import query_events
from session_log_mcp.db import get_conn

def test_query_filters(tmp_path):
    db_path = tmp_path / "test.db"

    def mock_get_conn(path=None):
        return get_conn(db_path)

    with patch("session_log_mcp.db.schema.get_conn", side_effect=mock_get_conn), \
         patch("session_log_mcp.tools.record.get_conn", side_effect=mock_get_conn), \
         patch("session_log_mcp.tools.query.get_conn", side_effect=mock_get_conn):

        from session_log_mcp.db.schema import ensure
        ensure(db_path)

        # Insert test data
        record_event(kind="test1", payload="p1", spec_id="100", session_id="s1", ts="2023-01-01T10:00:00Z")
        record_event(kind="test2", payload="p2", spec_id="100", session_id="s1", ts="2023-01-01T11:00:00Z")
        record_event(kind="test1", payload="p3", spec_id="101", session_id="s2", ts="2023-01-01T12:00:00Z")

        # Query by spec_id
        res = json.loads(query_events(spec_id="100"))["items"]
        assert len(res) == 2

        # Query by kind
        res = json.loads(query_events(kind="test1"))["items"]
        assert len(res) == 2

        # Query by session_id and kind
        res = json.loads(query_events(session_id="s1", kind="test1"))["items"]
        assert len(res) == 1
        assert res[0]["payload"] == "p1"

        # Test ordering
        res = json.loads(query_events())["items"]
        assert len(res) == 3
        # Should be descending ts
        assert res[0]["ts"] == "2023-01-01T12:00:00Z"

        # Test limit
        res = json.loads(query_events(limit=1))["items"]
        assert len(res) == 1
        assert res[0]["ts"] == "2023-01-01T12:00:00Z"
