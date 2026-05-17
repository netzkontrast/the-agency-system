from unittest.mock import patch, MagicMock

from jules_mcp.tools.bulk import jules_status_all, jules_approve_awaiting, jules_quota
import datetime

@patch("jules_mcp.tools.bulk._paginate")
def test_status_all_groups_by_state(mock_paginate):
    mock_paginate.return_value = (
        [
            {"id": "1", "state": "COMPLETED", "title": "t1"},
            {"id": "2", "state": "COMPLETED", "title": "t2"},
            {"id": "3", "state": "AWAITING_PLAN_APPROVAL", "title": "t3"}
        ],
        "", 1, False
    )
    
    res = jules_status_all(fields="id,state,title")
    assert "by_state" in res
    assert "COMPLETED" in res["by_state"]
    assert len(res["by_state"]["COMPLETED"]) == 2
    assert "AWAITING_PLAN_APPROVAL" in res["by_state"]
    assert len(res["by_state"]["AWAITING_PLAN_APPROVAL"]) == 1

@patch("jules_mcp.tools.bulk._paginate")
def test_status_all_trim_default(mock_paginate):
    mock_paginate.return_value = (
        [
            {"id": "1", "state": "COMPLETED", "title": "t1", "extra": "data", "should_drop": True}
        ],
        "", 1, False
    )
    
    res = jules_status_all()
    assert len(res["sessions"]) == 1
    session = res["sessions"][0]
    assert session == {"id": "1", "state": "COMPLETED", "title": "t1"}

@patch("jules_mcp.tools.bulk._paginate")
@patch("datetime.datetime")
def test_quota_counts_today_only(mock_datetime, mock_paginate):
    mock_now = MagicMock()
    mock_now.date.return_value.isoformat.return_value = "2023-01-15"
    mock_datetime.now.return_value = mock_now
    mock_datetime.timezone.utc = datetime.timezone.utc
    
    mock_paginate.return_value = (
        [
            {"id": "1", "createTime": "2023-01-15T10:00:00Z", "state": "IN_PROGRESS"},
            {"id": "2", "createTime": "2023-01-15T11:00:00Z", "state": "COMPLETED"},
            {"id": "3", "createTime": "2023-01-14T23:59:59Z", "state": "IN_PROGRESS"}
        ],
        "", 1, False
    )
    
    res = jules_quota()
    assert res["used_today"] == 2
    assert res["active_today"] == 1
    assert res["today_utc"] == "2023-01-15"
    assert res["newest_today_id"] == "2"
    
@patch("jules_mcp.tools.bulk.jules_status_all")
@patch("jules_mcp.tools.bulk.jules_approve")
def test_approve_awaiting_only_targets_correct_state(mock_approve, mock_status_all):
    mock_status_all.return_value = {
        "by_state": {
            "AWAITING_PLAN_APPROVAL": [
                {"id": "3", "state": "AWAITING_PLAN_APPROVAL", "title": "t3"}
            ],
            "COMPLETED": [
                {"id": "1", "state": "COMPLETED", "title": "t1"}
            ]
        }
    }
    mock_approve.return_value = {"ok": True, "session_id": "3"}
    
    res = jules_approve_awaiting()
    assert res["approved"] == ["3"]
    assert res["skipped"] == []
    assert res["errors"] == []
    mock_approve.assert_called_once_with(session_id="3")
