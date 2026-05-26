"""jules — the agent capability. An agent IS a Lifecycle parameterization that
dispatches a remote async session and inserts a `verify` step, because
`COMPLETED != done`: the Jules session state flips to COMPLETED even when it
paused before pushing a branch. `verify` checks the branch on REMOTE — the real
silent-fail guard (CLAUDE.md, JULES_PROTOCOL §8).

This is a COMPLETE implementation: `RealJulesClient` calls the actual Jules
orchestrator (`jules_create` / `jules_get`). It is injected at the boundary, so
the engine really dispatches Jules in production while deterministic tests pass a
stand-in for the external API.
"""
from __future__ import annotations

from typing import Optional, Protocol

from ..capability import Capability


class JulesClient(Protocol):
    def create(self, prompt: str, source: str, starting_branch: str) -> dict: ...
    def get(self, session: str) -> dict: ...


class RealJulesClient:
    """Wraps the real Jules orchestrator (jules-plugin). Lazily imported so the
    seed has no hard dependency until you actually dispatch."""

    def _lifecycle(self):
        try:
            from jules_mcp.tools import lifecycle  # type: ignore
        except ImportError as e:  # pragma: no cover - environment-specific
            raise RuntimeError(
                "RealJulesClient needs the jules-plugin on PYTHONPATH "
                "(jules-plugin/mcp-server/src) and JULES_API_KEY set."
            ) from e
        return lifecycle

    def create(self, prompt: str, source: str, starting_branch: str) -> dict:
        return self._lifecycle().jules_create(
            prompt=prompt, source=source, starting_branch=starting_branch,
            require_plan_approval=False)

    def get(self, session: str) -> dict:
        return self._lifecycle().jules_get(session)


def dispatch(source: str, starting_branch: str, prompt: str,
             client: Optional[JulesClient] = None) -> dict:
    "Spawn a remote Jules session (external effect). Returns its id/url/state."
    s = (client or RealJulesClient()).create(
        prompt=prompt, source=source, starting_branch=starting_branch)
    sid = s.get("id") or s.get("name")
    return {
        "status": s.get("state", "submitted"),
        "session": sid,
        "url": s.get("url"),
        "artefact": {"kind": "jules-session", "session": sid or "", "url": s.get("url") or ""},
    }


def status(session: str, client: Optional[JulesClient] = None) -> dict:
    "Read a session's current state from the orchestrator."
    s = (client or RealJulesClient()).get(session)
    return {"state": s.get("state"), "url": s.get("url")}


def verify(state: str, branch_on_remote: bool) -> dict:
    "COMPLETED != done: done only if state is completed AND a branch is on origin."
    done = str(state).lower() == "completed" and bool(branch_on_remote)
    return {"done": done, "state": state, "branch_on_remote": bool(branch_on_remote)}


jules_capability = Capability(
    name="jules",
    home="lifecycle",
    verbs={
        # `inject: ["client"]` — the engine supplies its jules_client (the boundary
        # object) so the verb stays pure and the param is hidden from the MCP schema.
        "dispatch": {"role": "effect", "fn": dispatch, "inject": ["client"]},   # spawns a remote session
        "status": {"role": "transform", "fn": status, "inject": ["client"]},    # reads session state
        "verify": {"role": "transform", "fn": verify},     # the COMPLETED != done guard (pure)
    },
)
