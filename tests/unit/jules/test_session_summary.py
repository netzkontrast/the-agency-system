"""Tests for jules_session_summary — Spec 101.

The summary tool wraps jules_get + jules_activities so the orchestrator
can poll the supervisory loop in one call. The contract is fixed: a dict
with exactly five keys.
"""
from unittest.mock import patch

import pytest

from agency_mcp.handlers.jules import lifecycle


EXPECTED_KEYS = {"state", "title", "last_5_activities", "pr_url", "patch_size_lines"}


def _fake_activity(kind: str, summary: str = "") -> dict:
    return {"id": f"act-{kind}", "originator": "agent", "kind": kind, "summary": summary}


def test_session_summary_returns_exactly_five_keys():
    """Anchor 101.1 — the result dict has EXACTLY the five canonical keys."""
    fake_session = {
        "id": "sid-abc",
        "state": "IN_PROGRESS",
        "title": "Spec 101 implementation",
        "outputs": [],
    }
    fake_activities = {
        "activities": [
            _fake_activity("planGenerated", "plan"),
            _fake_activity("agentMessaged", "msg1"),
            _fake_activity("agentMessaged", "msg2"),
            _fake_activity("agentMessaged", "msg3"),
            _fake_activity("agentMessaged", "msg4"),
            _fake_activity("agentMessaged", "msg5"),
        ],
        "nextPageToken": "",
    }

    with patch.object(lifecycle, "_request") as mock_request:
        # jules_get hits /v1alpha/sessions/{sid}; jules_activities hits
        # /v1alpha/sessions/{sid}/activities?... — return in that order.
        mock_request.side_effect = [fake_session, fake_activities]
        result = lifecycle.jules_session_summary("sid-abc")

    assert isinstance(result, dict), f"expected dict, got {type(result)!r}"
    assert set(result.keys()) == EXPECTED_KEYS, (
        f"expected keys {sorted(EXPECTED_KEYS)}, got {sorted(result.keys())}"
    )


def test_session_summary_slices_last_5_activities():
    """Anchor 101.1 — last_5_activities is min(5, total)."""
    fake_session = {
        "id": "sid-abc",
        "state": "IN_PROGRESS",
        "title": "Spec 101",
        "outputs": [],
    }
    # Six activities — slice should yield the most recent five (the API
    # returns newest-first per Jules v1alpha convention).
    fake_activities = {
        "activities": [_fake_activity("agentMessaged", f"msg{i}") for i in range(6)],
        "nextPageToken": "",
    }
    with patch.object(lifecycle, "_request") as mock_request:
        mock_request.side_effect = [fake_session, fake_activities]
        result = lifecycle.jules_session_summary("sid-abc")

    assert len(result["last_5_activities"]) == 5


def test_session_summary_fewer_than_five_activities():
    """Anchor 101.1 — length is min(5, total) even when fewer than 5 exist."""
    fake_session = {
        "id": "sid-abc",
        "state": "PLANNING",
        "title": "Spec 101",
        "outputs": [],
    }
    fake_activities = {
        "activities": [
            _fake_activity("planGenerated", "plan"),
            _fake_activity("agentMessaged", "msg"),
        ],
        "nextPageToken": "",
    }
    with patch.object(lifecycle, "_request") as mock_request:
        mock_request.side_effect = [fake_session, fake_activities]
        result = lifecycle.jules_session_summary("sid-abc")

    assert len(result["last_5_activities"]) == 2


def test_session_summary_propagates_state_and_title():
    fake_session = {
        "id": "sid-abc",
        "state": "AWAITING_PLAN_APPROVAL",
        "title": "Doc work",
        "outputs": [],
    }
    fake_activities = {"activities": [], "nextPageToken": ""}
    with patch.object(lifecycle, "_request") as mock_request:
        mock_request.side_effect = [fake_session, fake_activities]
        result = lifecycle.jules_session_summary("sid-abc")

    assert result["state"] == "AWAITING_PLAN_APPROVAL"
    assert result["title"] == "Doc work"
    assert result["last_5_activities"] == []


def test_session_summary_no_pr_returns_none_pr_url():
    fake_session = {
        "id": "sid-abc",
        "state": "COMPLETED",
        "title": "no PR",
        "outputs": [],
    }
    fake_activities = {"activities": [], "nextPageToken": ""}
    with patch.object(lifecycle, "_request") as mock_request:
        mock_request.side_effect = [fake_session, fake_activities]
        result = lifecycle.jules_session_summary("sid-abc")

    assert result["pr_url"] is None


def test_session_summary_includes_pr_url_when_present():
    fake_session = {
        "id": "sid-abc",
        "state": "COMPLETED",
        "title": "with PR",
        "outputs": [
            {"pullRequest": {"url": "https://github.com/example/repo/pull/42"}}
        ],
    }
    fake_activities = {"activities": [], "nextPageToken": ""}
    with patch.object(lifecycle, "_request") as mock_request:
        mock_request.side_effect = [fake_session, fake_activities]
        result = lifecycle.jules_session_summary("sid-abc")

    assert result["pr_url"] == "https://github.com/example/repo/pull/42"


def test_session_summary_patch_size_lines_zero_when_no_patch():
    fake_session = {
        "id": "sid-abc",
        "state": "IN_PROGRESS",
        "title": "no patch",
        "outputs": [],
    }
    fake_activities = {"activities": [], "nextPageToken": ""}
    with patch.object(lifecycle, "_request") as mock_request:
        mock_request.side_effect = [fake_session, fake_activities]
        result = lifecycle.jules_session_summary("sid-abc")

    assert result["patch_size_lines"] == 0


def test_session_summary_patch_size_lines_counts_added_and_removed():
    """Patch size = lines_added + lines_removed in the most recent activity
    artifact's gitPatch.unidiffPatch. Mirrors the parsing in patches.py."""
    fake_session = {
        "id": "sid-abc",
        "state": "COMPLETED",
        "title": "with patch",
        "outputs": [],
    }
    patch_text = (
        "diff --git a/foo.py b/foo.py\n"
        "--- a/foo.py\n"
        "+++ b/foo.py\n"
        "@@\n"
        "+added line 1\n"
        "+added line 2\n"
        "-removed line\n"
    )
    fake_activities = {
        "activities": [
            {
                "id": "act-1",
                "createTime": "2026-05-18T12:00:00Z",
                "artifacts": [
                    {"changeSet": {"gitPatch": {"unidiffPatch": patch_text}}}
                ],
                "agentMessaged": {},
            }
        ],
        "nextPageToken": "",
    }
    with patch.object(lifecycle, "_request") as mock_request:
        mock_request.side_effect = [fake_session, fake_activities]
        result = lifecycle.jules_session_summary("sid-abc")

    # 2 added + 1 removed = 3
    assert result["patch_size_lines"] == 3
