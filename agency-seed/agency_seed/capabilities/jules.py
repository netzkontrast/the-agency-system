"""jules — the agent capability (home = Lifecycle: an agent IS a lifecycle
parameterization). Encodes the hard-won lesson: `COMPLETED != done`. `patch`
returns COMPLETED but may not have pushed a branch; `verify` is the inserted
observe-step that catches the silent-fail.
"""
from __future__ import annotations

from ..capability import Capability


def patch(spec: str, pushed: bool = False) -> dict:
    # Simulates a Jules session that finished its turn ("COMPLETED") but may have
    # paused before pushing the branch.
    return {
        "status": "COMPLETED",
        "branch_pushed": pushed,
        "artefact": {"kind": "patch", "spec": spec, "files": 1},
    }


def verify(branch_pushed: bool) -> dict:
    # COMPLETED != done: only a real branch on remote means done.
    return {"done": bool(branch_pushed)}


jules_capability = Capability(
    name="jules",
    home="lifecycle",
    verbs={
        "patch": {"role": "act", "fn": patch},
        "verify": {"role": "check", "fn": verify},
    },
)
