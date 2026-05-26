"""Micro-step skill walker.

A skill is a Lifecycle of ordered Phases (from a schema like
`ontology.ALBUM_CONCEPT_SKILL`). The walker is the complete implementation of
"real micro-step skills":

- **Progressive disclosure / token efficiency:** `current()` returns ONLY the
  current phase's spec (its required outputs) — never the whole skill.
- **Strict per-phase validation:** `submit()` rejects a phase whose required
  outputs are missing.
- **Hard gate:** a phase marked `gate: hard` (the conceptualizer's Phase 7)
  blocks at `input-required` until an explicit confirmation — the elicit gate.
- **Provenance:** every phase is recorded as a `Phase` node, edged into the
  `Skill` run (`HAS_PHASE`), the intent (`SERVES`), and the prior phase
  (`PRECEDES`). A skill run IS provenance.
"""
from __future__ import annotations

from typing import Optional

from .memory import Memory


class SkillRun:
    def __init__(self, memory: Memory, intent_id: str, schema: dict):
        self.memory = memory
        self.intent_id = intent_id
        self.schema = schema
        self.phases = schema["phases"]
        self.i = 0
        self.skill_id = memory.record("Skill", {"name": schema["name"], "kind": schema["kind"]})
        memory.link(self.skill_id, intent_id, "SERVES")
        self._prev_phase: Optional[str] = None

    @property
    def done(self) -> bool:
        return self.i >= len(self.phases)

    def current(self) -> Optional[dict]:
        """Progressive disclosure: only the current phase's spec (required outputs)."""
        if self.done:
            return None
        p = self.phases[self.i]
        return {"index": p["index"], "name": p["name"],
                "produces": list(p["produces"]), "gate": p.get("gate")}

    def submit(self, outputs: dict, confirmed: bool = False) -> dict:
        """Advance one phase. Rejects missing required outputs; a hard gate needs
        an explicit confirmation (it pauses at `input-required` otherwise)."""
        if self.done:
            raise RuntimeError("skill run already complete")
        p = self.phases[self.i]
        missing = [f for f in p["produces"] if outputs.get(f) in (None, "")]
        if missing:
            raise ValueError(f"phase {p['name']!r} missing required outputs: {missing}")
        if p.get("gate") == "hard" and not confirmed:
            return {"status": "input-required", "phase": p["name"], "gate": "hard"}
        phase_id = self.memory.record("Phase", {
            "skill": self.schema["name"], "index": p["index"], "name": p["name"],
            "produces": ",".join(p["produces"]),
        })
        self.memory.link(self.skill_id, phase_id, "HAS_PHASE")
        self.memory.link(phase_id, self.intent_id, "SERVES")
        if self._prev_phase:
            self.memory.link(self._prev_phase, phase_id, "PRECEDES")
        self._prev_phase = phase_id
        self.i += 1
        return {"status": "completed" if self.done else "working", "phase": p["name"]}
