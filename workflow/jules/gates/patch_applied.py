"""Callable evaluator for the `patch-applied` gate.

Returns ok=True when the JulesSession is in one of the two states from
which phase 08 (integrate) may legally run:

* ``VERIFIED``         — clean landing, integrate is a no-op finaliser.
* ``PATCH_EXTRACTED``  — silent-fail path, integrate applies the patch.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from agentic.jules.handlers._session_state import load_session


_PRE_INTEGRATE_STATES = {"VERIFIED", "PATCH_EXTRACTED"}


def _session_id(envelope_state: Dict[str, Any]) -> Optional[str]:
    inputs = envelope_state.get("inputs") if isinstance(envelope_state, dict) else None
    if isinstance(inputs, dict):
        sid = inputs.get("session_id")
        if isinstance(sid, str) and sid:
            return sid
    return None


def evaluate(envelope_state: Dict[str, Any], args: Dict[str, Any] | None = None) -> Dict[str, str]:
    sid = _session_id(envelope_state)
    if not sid:
        return {"ok": False, "message": "patch-applied gate needs inputs.session_id"}

    session = load_session(sid)
    if session is None:
        return {"ok": False, "message": f"no JulesSession node for session_id={sid}"}

    state = session.get("state", "DISPATCHED")
    if state in _PRE_INTEGRATE_STATES:
        return {"ok": True, "message": f"local state {state} permits integrate"}

    return {
        "ok": False,
        "message": f"session state {state} not in {sorted(_PRE_INTEGRATE_STATES)}",
    }
