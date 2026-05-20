"""Callable evaluator for the `research-complete` gate.

Returns ok=True when the ontology contains at least one ``Finding``
node whose ``topic`` matches the envelope's input topic. Falls back to
counting all Finding nodes when no topic was supplied — this matches
the gate's plain-English description ("at least one Finding exists").

Spec 09 cross-row dispatch will eventually let this gate query the
context column via the driver REGISTRY; until then a direct graph
query is the canonical contract.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from context import get_store


def _topic(envelope_state: Dict[str, Any]) -> Optional[str]:
    inputs = envelope_state.get("inputs") if isinstance(envelope_state, dict) else None
    if isinstance(inputs, dict):
        t = inputs.get("topic")
        if isinstance(t, str) and t:
            return t
    return None


def _count_findings(topic: Optional[str]) -> int:
    """Count Finding nodes for a topic (or all of them when topic is None).

    Tolerates the two GraphQLite property-encoding shapes the v0.1 store
    surfaces (``properties`` dict or raw-SQLite ``payload`` string) so
    the gate works both before and after spec 08-v1 fallback removal.
    """
    g = get_store()
    rows = g.query("MATCH (f:Finding) RETURN f", params={})
    count = 0
    for row in rows:
        node = row.get("f", row) if isinstance(row, dict) else None
        if not isinstance(node, dict):
            continue
        props = node.get("properties") or node.get("payload") or node
        if isinstance(props, str):
            import json
            try:
                props = json.loads(props)
            except Exception:
                continue
        if not isinstance(props, dict):
            continue
        if topic is None or props.get("topic") == topic:
            count += 1
    return count


def evaluate(envelope_state: Dict[str, Any], args: Dict[str, Any] | None = None) -> Dict[str, str]:
    topic = _topic(envelope_state)
    n = _count_findings(topic)
    if n > 0:
        scope = f"topic={topic!r}" if topic else "any topic"
        return {"ok": True, "message": f"{n} Finding node(s) recorded for {scope}"}
    scope = f"topic={topic!r}" if topic else "any topic"
    return {
        "ok": False,
        "message": f"no Finding nodes recorded for {scope} yet — run research first",
    }
