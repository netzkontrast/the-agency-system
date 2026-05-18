"""Tests for jules_pr_url — Spec 101.

Thin wrapper that returns the PR URL string when a session has opened a
PR, or None when none exists. Sourced from Session.outputs[].pullRequest.
"""
from unittest.mock import patch

import pytest

from agency_mcp.handlers.jules import lifecycle


def test_pr_url_returns_none_when_no_pr():
    """Anchor 101.2 — sessions without a PR return None."""
    fake_session = {
        "id": "sid-no-pr",
        "state": "IN_PROGRESS",
        "title": "no PR yet",
        "outputs": [],
    }
    with patch.object(lifecycle, "_request", return_value=fake_session):
        assert lifecycle.jules_pr_url("sid-no-pr") is None


def test_pr_url_returns_none_when_outputs_missing():
    fake_session = {
        "id": "sid-empty",
        "state": "PLANNING",
        "title": "no outputs key",
    }
    with patch.object(lifecycle, "_request", return_value=fake_session):
        assert lifecycle.jules_pr_url("sid-empty") is None


def test_pr_url_returns_url_string_when_pr_exists():
    """Anchor 101.2 — sessions with a PR return its URL."""
    fake_session = {
        "id": "sid-with-pr",
        "state": "COMPLETED",
        "title": "PR opened",
        "outputs": [
            {"pullRequest": {"url": "https://github.com/example/repo/pull/7"}}
        ],
    }
    with patch.object(lifecycle, "_request", return_value=fake_session):
        assert (
            lifecycle.jules_pr_url("sid-with-pr")
            == "https://github.com/example/repo/pull/7"
        )
