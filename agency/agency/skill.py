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
    def __init__(self, memory: Memory, intent_id: str, schema: dict, registry=None):
        self.memory = memory
        self.intent_id = intent_id
        self.schema = schema
        self.phases = schema["phases"]
        self.registry = registry            # required if any phase is executable (has `invoke`)
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
        return {"index": p["index"], "name": p["name"], "produces": list(p["produces"]),
                "inputs": list(p.get("inputs", [])), "gate": p.get("gate")}

    def submit(self, outputs: Optional[dict] = None, confirmed: bool = False) -> dict:
        """Advance one phase. An executable phase (`invoke`) runs a REAL capability
        verb (recorded as an Invocation) and uses its output to satisfy the schema;
        a plain phase consumes the submitted `outputs`. Missing required outputs
        raise; a hard gate pauses at `input-required` until confirmed."""
        if self.done:
            raise RuntimeError("skill run already complete")
        p = self.phases[self.i]
        outputs = dict(outputs or {})
        inv_id = None
        if "invoke" in p:
            if self.registry is None:
                raise RuntimeError(f"phase {p['name']!r} is executable but no registry was given")
            spec = p["invoke"]
            args = {k: outputs[k] for k in p.get("inputs", []) if k in outputs}
            result, inv_id = self.registry.invoke(
                self.memory, self.intent_id, spec["capability"], spec["verb"], **args)
            val = result.get("result", result) if isinstance(result, dict) else result
            outputs[p["produces"][0]] = val                  # real tool output satisfies the schema
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
        if inv_id:
            self.memory.link(phase_id, inv_id, "PRECEDES")   # the phase owns its real invocation
        self._prev_phase = phase_id
        self.i += 1
        return {"status": "completed" if self.done else "working", "phase": p["name"]}

