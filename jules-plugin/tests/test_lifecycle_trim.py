import pytest
from unittest.mock import patch, MagicMock

import sys
fastmcp_mock = MagicMock()
sys.modules.setdefault('fastmcp', fastmcp_mock)

from jules_mcp.tools.lifecycle import jules_list, jules_get, jules_activities, jules_plan

@patch('jules_mcp.tools.lifecycle._request')
def test_jules_list_trim(mock_request):
    mock_request.return_value = {
        "sessions": [{"id": "1", "state": "A", "title": "B", "url": "U"}],
        "nextPageToken": ""
    }
    
    # default trim
    res = jules_list()
    assert res["sessions"] == [{"id": "1", "state": "A", "title": "B"}]
    
    # fields="*"
    res_all = jules_list(fields="*")
    assert res_all["sessions"] == [{"id": "1", "state": "A", "title": "B", "url": "U"}]

@patch('jules_mcp.tools.lifecycle._request')
def test_jules_get_trim(mock_request):
    mock_request.return_value = {"id": "1", "name": "sessions/1", "state": "A", "title": "B"}
    
    # default trim
    res = jules_get("1")
    assert res == {"id": "1", "state": "A", "title": "B"}
    
    # fields="*"
    res_all = jules_get("1", fields="*")
    assert res_all == {"id": "1", "state": "A", "title": "B", "url": "", "has_outputs": False, "require_plan_approval": None, "source": None, "branch": None}

@patch('jules_mcp.tools.lifecycle._request')
def test_jules_activities_summary(mock_request):
    mock_request.return_value = {
        "activities": [{
            "name": "a1",
            "agentMessaged": {"agentMessage": "hello"},
            "extra": "discarded"
        }],
        "nextPageToken": ""
    }
    
    # summary_only=True (default)
    res = jules_activities("1")
    assert len(res["activities"]) == 1
    assert res["activities"][0] == {
        "id": "a1",
        "originator": None,
        "kind": "agentMessaged",
        "summary": "hello"
    }
    
    # summary_only=False
    res_full = jules_activities("1", summary_only=False)
    assert len(res_full["activities"]) == 1
    assert "agentMessaged" in res_full["activities"][0]
    assert "extra" in res_full["activities"][0]

@patch('jules_mcp.tools.lifecycle._paginate')
def test_jules_plan_trim(mock_paginate):
    mock_paginate.return_value = ([{
        "planGenerated": {
            "plan": {
                "steps": [
                    {"title": "step1", "description": "desc1"},
                    {"title": "step2", "description": "desc2"}
                ]
            }
        }
    }], "", 1, False)
    
    # include_descriptions=False (default)
    res = jules_plan("1")
    assert res["steps"][0] == {"title": "step1"}
    
    # include_descriptions=True
    res_full = jules_plan("1", include_descriptions=True)
    assert res_full["steps"][0] == {"title": "step1", "description": "desc1"}
