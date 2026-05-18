"""Tests for jules_create's initial_messages parameter and the 404-on-fresh-session
retry, plus a smoke test that the four jules-bulk shim imports resolve.

L08 + dispatch friction (2026-05-18): jules_message returns 404 immediately
after jules_create — the upstream session isn't ready to receive messages
yet. The orchestrator's workaround was a manual retry loop. This module
bakes the retry into jules_create itself via initial_messages, so the
common "create then send rebase instruction" pattern is one call instead
of three.
"""
from unittest.mock import patch, MagicMock
import importlib
import sys

import pytest

fastmcp_mock = MagicMock()
sys.modules.setdefault("fastmcp", fastmcp_mock)

from jules_mcp.tools.lifecycle import jules_create  # noqa: E402
from jules_mcp.api import JulesAPIError  # noqa: E402


def _stub_create_response(sid: str = "abc") -> dict:
    return {"id": sid, "name": f"sessions/{sid}", "state": "?", "title": "t", "url": f"u/{sid}"}


# Pre-resolved source string — bypasses _resolve_github_source HTTP roundtrip.
SRC = "sources/abc123"


@patch("jules_mcp.tools.lifecycle.sessions_state", None)
@patch("jules_mcp.tools.lifecycle.time.sleep", lambda *_a, **_k: None)
@patch("jules_mcp.tools.lifecycle._request")
def test_no_initial_messages_keeps_single_request(mock_request):
    mock_request.return_value = _stub_create_response()
    res = jules_create(prompt="p", source="sources/abc123", starting_branch="main")
    assert mock_request.call_count == 1
    assert "initial_messages_sent" not in res
    assert "initial_messages_failed" not in res


@patch("jules_mcp.tools.lifecycle.sessions_state", None)
@patch("jules_mcp.tools.lifecycle.time.sleep", lambda *_a, **_k: None)
@patch("jules_mcp.tools.lifecycle._request")
def test_empty_initial_messages_keeps_single_request(mock_request):
    mock_request.return_value = _stub_create_response()
    res = jules_create(prompt="p", source="sources/abc123", starting_branch="main", initial_messages=[])
    assert mock_request.call_count == 1
    assert res.get("initial_messages_sent", []) == []


@patch("jules_mcp.tools.lifecycle.sessions_state", None)
@patch("jules_mcp.tools.lifecycle.time.sleep", lambda *_a, **_k: None)
@patch("jules_mcp.tools.lifecycle._request")
def test_initial_messages_sends_each_after_create(mock_request):
    mock_request.side_effect = [_stub_create_response("s1"), {}, {}]
    res = jules_create(
        prompt="p", source="sources/abc123", starting_branch="main",
        initial_messages=["first", "second"],
    )
    # 1 create + 2 sendMessage
    assert mock_request.call_count == 3
    paths = [c.args[1] for c in mock_request.call_args_list]
    assert paths[0] == "/v1alpha/sessions"
    assert paths[1].endswith(":sendMessage")
    assert paths[2].endswith(":sendMessage")
    # The two payloads carry the message prompts in order
    bodies = [c.kwargs.get("body") or c.args[2] if len(c.args) > 2 else c.kwargs.get("body") for c in mock_request.call_args_list]
    assert bodies[1] == {"prompt": "first"}
    assert bodies[2] == {"prompt": "second"}
    assert res["initial_messages_sent"] == ["first", "second"]
    assert res.get("initial_messages_failed", []) == []


@patch("jules_mcp.tools.lifecycle.sessions_state", None)
@patch("jules_mcp.tools.lifecycle.time.sleep", lambda *_a, **_k: None)
@patch("jules_mcp.tools.lifecycle._request")
def test_initial_message_retries_on_404_then_succeeds(mock_request):
    create_resp = _stub_create_response("s2")
    err = JulesAPIError(404, "404 Not Found — resource does not exist.", "")
    # create succeeds; first sendMessage 404s; second sendMessage succeeds
    mock_request.side_effect = [create_resp, err, {}]
    res = jules_create(
        prompt="p", source="sources/abc123", starting_branch="main",
        initial_messages=["rebase pls"],
    )
    assert mock_request.call_count == 3
    assert res["initial_messages_sent"] == ["rebase pls"]
    assert res.get("initial_messages_failed", []) == []


@patch("jules_mcp.tools.lifecycle.sessions_state", None)
@patch("jules_mcp.tools.lifecycle.time.sleep", lambda *_a, **_k: None)
@patch("jules_mcp.tools.lifecycle._request")
def test_initial_message_gives_up_after_max_attempts_without_raising(mock_request):
    create_resp = _stub_create_response("s3")
    err = JulesAPIError(404, "404 Not Found — resource does not exist.", "")
    # create succeeds; every sendMessage 404s — must NOT raise, must record failure
    mock_request.side_effect = [create_resp] + [err] * 20
    res = jules_create(
        prompt="p", source="sources/abc123", starting_branch="main",
        initial_messages=["never lands"],
    )
    # Returned successfully (no raise)
    assert res["id"] == "s3"
    assert res.get("initial_messages_sent", []) == []
    assert res["initial_messages_failed"] == [
        {"message": "never lands", "status": 404, "attempts": 6},
    ]


@patch("jules_mcp.tools.lifecycle.sessions_state", None)
@patch("jules_mcp.tools.lifecycle.time.sleep", lambda *_a, **_k: None)
@patch("jules_mcp.tools.lifecycle._request")
def test_non_404_error_during_message_is_not_retried(mock_request):
    create_resp = _stub_create_response("s4")
    err = JulesAPIError(500, "5xx Server Error (500) — retryable.", "")
    mock_request.side_effect = [create_resp, err]
    res = jules_create(
        prompt="p", source="sources/abc123", starting_branch="main",
        initial_messages=["boom"],
    )
    # 1 create + 1 sendMessage attempt (no retry on non-404)
    assert mock_request.call_count == 2
    assert res.get("initial_messages_failed", []) == [
        {"message": "boom", "status": 500, "attempts": 1},
    ]


def test_bulk_shim_imports_resolve():
    """Smoke test for the jules-bulk shim's four import sites.

    Each subcommand in bin/jules-bulk runs an inline Python heredoc that
    imports a top-level function. Until 2026-05-18 those imports were
    sourced from `jules_mcp.server`, where the functions are registered as
    FastMCP tools but NOT re-exported as module attributes. Result: the
    shim crashed with "module 'jules_mcp.server' has no attribute …".

    Pin the fix: every function the shim invokes must be importable from
    the exact submodule the fix points to. If a future refactor moves
    them, this test fails and the shim's import paths must follow.
    """
    from jules_mcp.tools.lifecycle import jules_create as _jc  # noqa: F401
    from jules_mcp.tools.bulk import (  # noqa: F401
        jules_status_all as _jsa,
        jules_approve_awaiting as _jaa,
        jules_quota as _jq,
    )
