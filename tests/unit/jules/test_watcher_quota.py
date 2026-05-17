import pytest
from unittest.mock import patch
import time

def test_watcher_quota_semantics():
    from agency_mcp.handlers.jules.lifecycle import jules_start_watcher, jules_watcher_status

    # We will mock the quota tracker
    with patch("agency_mcp.handlers.jules._shared.get_active_watchers_count", return_value=5), \
         patch("agency_mcp.handlers.jules._shared.get_watcher_quota", return_value=5):

        res = jules_start_watcher()
        assert res.get("ok") is False
        assert res.get("reason") == "quota_exceeded"

        status = jules_watcher_status()
        assert status.get("running") is True
        assert status.get("quota_remaining") == 0
