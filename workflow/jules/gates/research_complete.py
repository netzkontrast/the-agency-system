"""Callable evaluator for the `research-complete` gate.

v0.1 placeholder. The real implementation will query the ontology for
``Finding`` nodes matching the envelope's topic and emit a
``SATISFIES_PHASE`` edge from the gate's resolved artefact id to
``phase:jules/01`` when that count is non-zero. That work is gated on
two pieces still in flight:

* ``context._drivers.REGISTRY`` graduates to the canonical dispatch
  surface (spec 08-v1 §FR3) — the gate needs a stable way to ask the
  driver for the Finding bytes when the on-disk fallback isn't enough.
* Cross-row dispatch (spec 09) — the gate must hand control back to
  the row that owns the next phase without bypassing the harness.

Until both land, this evaluator returns ``ok=True`` unconditionally so
the synthesize phase doesn't deadlock on a graph the v0.1 base layer
can't yet populate exhaustively. The gate YAML's ``on_success.emit_edge``
remains the source of truth for the eventual edge wiring.
"""

from __future__ import annotations

from typing import Any, Dict


def evaluate(envelope_state: Dict[str, Any], args: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Return the gate's pass/fail verdict.

    Args:
        envelope_state: The PhaseStateEnvelope (or a slice of it) handed
            in by ``workflow._runner.gate.evaluate_gate``.
        args: Optional evaluator arguments from the gate YAML's
            ``evaluator.args`` field. Unused in v0.1.

    Returns:
        A dict with exactly ``{"ok": bool, "message": str}`` per the
        contract enforced by ``workflow._runner.gate.evaluate_gate``.
    """
    return {
        "ok": True,
        "message": "v0.1 placeholder — Finding-count check arrives with spec 09 cross-row dispatch.",
    }
