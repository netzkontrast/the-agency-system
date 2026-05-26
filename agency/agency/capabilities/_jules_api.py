"""Minimal, self-contained Jules REST client (vendored into the agency plugin).

A focused port of the legacy jules-orchestrator MCP server's HTTP layer + the
two calls the `jules` capability needs — `jules_create` and `jules_get`. Built on
`httpx` (the HTTP client the FastMCP stack already ships), not a hand-rolled
stdlib transport. The agency plugin owns its Jules integration; it does not depend
on the legacy orchestrator package.

Auth: set `JULES_API_KEY` in the environment. Base URL overridable via
`JULES_API_BASE_URL` (default `https://jules.googleapis.com`).
"""
from __future__ import annotations

import os
from typing import Any, Optional

import httpx

BASE_URL = os.environ.get("JULES_API_BASE_URL", "https://jules.googleapis.com")


class JulesAPIError(RuntimeError):
    """Non-2xx from the Jules REST API; carries the HTTP status code."""

    def __init__(self, status: int, message: str, body: str = ""):
        super().__init__(message)
        self.status = status
        self.body = body


def _api_key() -> str:
    key = os.environ.get("JULES_API_KEY", "")
    if not key:
        raise RuntimeError(
            "JULES_API_KEY is not set. Export it in the shell that launched the "
            "engine, then retry."
        )
    return key


def _translate_http_error(code: int, body: str) -> str:
    mapping = {
        400: "400 Bad Request — malformed payload. Body: ",
        401: "401 Unauthorized — JULES_API_KEY rejected. Re-export the key.",
        403: "403 Permission Denied — Jules cannot access the source. Connect the GitHub repo via the Jules GitHub app.",
        404: "404 Not Found — resource does not exist.",
        405: "405 Method Not Allowed — endpoint exists but does not accept this verb.",
        409: "409 Conflict — illegal state transition. Check current session state first.",
        429: "429 Quota Exceeded — pause polling and check billing/quota.",
    }
    if 500 <= code < 600:
        return f"5xx Server Error ({code}) — retryable. Body: {body[:300]}"
    base = mapping.get(code, f"HTTP {code}")
    if code == 400 and body:
        return base + body[:500]
    return base


def _request(method: str, path: str, body: Optional[dict] = None,
             params: Optional[dict] = None) -> dict:
    headers = {"x-goog-api-key": _api_key()}
    with httpx.Client(base_url=BASE_URL, timeout=60) as client:
        resp = client.request(method, path, json=body, params=params, headers=headers)
    if resp.status_code >= 400:
        raise JulesAPIError(resp.status_code,
                            _translate_http_error(resp.status_code, resp.text), resp.text)
    return resp.json() if resp.text else {}


def _paginate(path: str, params: dict, max_pages: int = 10) -> list[dict]:
    items: list[dict] = []
    token = ""
    pages = 0
    array_key: Optional[str] = None
    while pages < max_pages:
        q = dict(params)
        if token:
            q["pageToken"] = token
        raw = _request("GET", path, params=q)
        pages += 1
        if array_key is None:
            array_key = next((k for k, v in raw.items() if isinstance(v, list)), None)
            if array_key is None:
                break
        items.extend(raw.get(array_key, []) or [])
        token = raw.get("nextPageToken", "")
        if not token:
            break
    return items


def _short_id(name_or_id: str) -> str:
    """Accept 'sessions/123' or '123' and return '123'."""
    return name_or_id.rsplit("/", 1)[-1]


def _resolve_github_source(owner: str, repo: str) -> dict:
    """Resolve a GitHub owner/repo to its opaque `sources/{id}` name (not
    documented; must be looked up via sources.list)."""
    for s in _paginate("/v1alpha/sources", {"pageSize": 100}):
        gh = s.get("githubRepo") or {}
        if gh.get("owner") == owner and gh.get("repo") == repo:
            return {"source": s.get("name", ""), "github": {"owner": owner, "repo": repo}}
    return {"error": (f"no Jules source connected for github.com/{owner}/{repo}. "
                      "Connect the repository via the Jules GitHub app, then retry.")}


def _coerce_source(source: str) -> str:
    """Translate 'sources/<id>' | 'owner/repo' | a github URL into the opaque
    `sources/<id>` form Jules expects."""
    s = (source or "").strip()
    if not s:
        raise RuntimeError("source is required ('sources/<id>', 'owner/repo', or a GitHub URL).")
    if s.startswith("sources/") and s.count("/") == 1:
        return s
    owner = repo = None
    if s.startswith("sources/github/"):
        rest = s[len("sources/github/"):]
        if rest.count("/") == 1:
            owner, repo = rest.split("/", 1)
    elif "github.com" in s:
        path = s.split("github.com", 1)[1].lstrip(":/").rstrip("/")
        if path.endswith(".git"):
            path = path[:-4]
        parts = path.split("/")
        if len(parts) >= 2:
            owner, repo = parts[0], parts[1]
    elif "/" in s:
        parts = s.split("/")
        if len(parts) == 2:
            owner, repo = parts
    if owner and repo:
        resolved = _resolve_github_source(owner, repo)
        if "error" in resolved:
            raise RuntimeError(resolved["error"])
        return resolved["source"]
    raise RuntimeError(f"could not parse source {source!r}.")


def jules_create(prompt: str, source: str, starting_branch: str,
                 title: str = "", require_plan_approval: bool = True,
                 auto_create_pr: bool = False) -> dict:
    """Create a Jules session. Returns the session resource (id, state, url, ...)."""
    body: dict[str, Any] = {
        "prompt": prompt,
        "sourceContext": {
            "source": _coerce_source(source),
            "githubRepoContext": {"startingBranch": starting_branch},
        },
        "requirePlanApproval": bool(require_plan_approval),
    }
    if title:
        body["title"] = title
    if auto_create_pr:
        body["automationMode"] = "AUTO_CREATE_PR"
    return _request("POST", "/v1alpha/sessions", body)


def jules_get(session_id: str) -> dict:
    """Fetch a session's current state + metadata."""
    s = _request("GET", f"/v1alpha/sessions/{_short_id(session_id)}")
    return {
        "id": s.get("id") or _short_id(s.get("name", "")),
        "state": s.get("state"),
        "title": s.get("title", ""),
        "source": (s.get("sourceContext") or {}).get("source"),
        "branch": ((s.get("sourceContext") or {}).get("githubRepoContext") or {}).get("startingBranch"),
        "url": s.get("url", ""),
        "has_outputs": bool(s.get("outputs")),
    }
