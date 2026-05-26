"""Intent — the human-owned root (why/what merged; deliverable is an attribute).

capture -> confirm -> (amend via supersede). Everything edges back here via
SERVES. why/what are NOT two domains: a deliverable change with the purpose held
is just an attribute change on one Intent (the panel's finding).
"""
from __future__ import annotations

from .memory import Memory


class Intent:
    def __init__(self, memory: Memory):
        self.m = memory

    def capture(self, purpose: str, deliverable: str, acceptance: str) -> str:
        return self.m.record("Intent", {
            "purpose": purpose,
            "deliverable": deliverable,
            "acceptance": acceptance,
            "status": "draft",
        })

    def confirm(self, intent_id: str) -> str:
        # in place: confirming doesn't fork identity, so SERVES edges stay stable
        self.m.update(intent_id, {"status": "confirmed"})
        return intent_id

    def amend(self, intent_id: str, **changes) -> str:
        # the *what* changes while the *why* holds — one bi-temporal supersede,
        # so the prior version keeps its valid window (as-of reconstruction).
        return self.m.supersede(intent_id, changes)
