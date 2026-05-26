"""jules — the agent capability. An agent IS a Lifecycle parameterization that
dispatches a remote async session and inserts a `verify` step, because
`COMPLETED != done`: the Jules session state flips to COMPLETED even when it
paused before pushing a branch. `verify` checks the branch on REMOTE — the
silent-fail guard (CLAUDE.md, JULES_PROTOCOL §8).

The capability's boundary is a `JulesBackend` (a Protocol). The default backend,
`JulesClient`, talks to the real Jules REST API via the vendored `_jules_api`
client. The backend is injected, so the engine really dispatches Jules in
production while deterministic tests inject a stand-in.
"""
from __future__ import annotations

from typing import Optional, Protocol

from ..capability import Capability


class JulesBackend(Protocol):
    """The external boundary the `jules` capability talks to."""
    def create(self, prompt: str, source: str, starting_branch: str) -> dict: ...
    def get(self, session: str) -> dict: ...


class JulesClient:
    """The default `jules` backend — the real Jules REST API via the vendored
    `_jules_api` client. Needs `JULES_API_KEY` (checked at call time)."""

    def create(self, prompt: str, source: str, starting_branch: str) -> dict:
        from . import _jules_api
        return _jules_api.jules_create(
            prompt=prompt, source=source, starting_branch=starting_branch,
            require_plan_approval=False)

    def get(self, session: str) -> dict:
        from . import _jules_api
        return _jules_api.jules_get(session)


def dispatch(source: str, starting_branch: str, prompt: str,
             client: Optional[JulesBackend] = None) -> dict:
    "Spawn a remote Jules session (external effect). Returns its id/url/state."
    s = (client or JulesClient()).create(
        prompt=prompt, source=source, starting_branch=starting_branch)
    sid = s.get("id") or s.get("name")
    return {
        "status": s.get("state", "submitted"),
        "session": sid,
        "url": s.get("url"),
        "artefact": {"kind": "jules-session", "session": sid or "", "url": s.get("url") or ""},
    }


def status(session: str, client: Optional[JulesBackend] = None) -> dict:
    "Read a session's current state from the backend."
    s = (client or JulesClient()).get(session)
    return {"state": s.get("state"), "url": s.get("url")}


def verify(state: str, branch_on_remote: bool) -> dict:
    "COMPLETED != done: done only if state is completed AND a branch is on origin."
    done = str(state).lower() == "completed" and bool(branch_on_remote)
    return {"done": done, "state": state, "branch_on_remote": bool(branch_on_remote)}


jules_capability = Capability(
    name="jules",
    home="lifecycle",
    verbs={
        # `inject: ["client"]` — the engine supplies its jules backend (the boundary
        # object) so the verb stays pure and the param is hidden from the MCP schema.
        "dispatch": {"role": "effect", "fn": dispatch, "inject": ["client"]},   # spawns a remote session
        "status": {"role": "transform", "fn": status, "inject": ["client"]},    # reads session state
        "verify": {"role": "transform", "fn": verify},     # the COMPLETED != done guard (pure)
    },
)
