"""PhaseStateEnvelope persistence via the real :class:`context.Store`.

Spec 07-v1 §FR4 — the ``_MockContext`` seam from the v0 base layer is
gone. Continuation lives only as a ``Continuation`` graph node, reached
through the process-singleton :func:`context.get_store`. Callers (the
pipeline runner) MUST NOT construct ``Store()`` directly.

Spec 07-v1 §FR7 — the TTL sweep deletes ``Continuation`` nodes whose
``created_at_epoch`` is older than 30 days. Best-effort: a per-delete
failure logs a warning and does NOT abort boot.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Literal, Optional, TypedDict

logger = logging.getLogger(__name__)

THIRTY_DAYS_S = 30 * 24 * 3600


class PhaseStateEnvelope(TypedDict):
    status: Literal["running", "blocked_on_gate", "blocked_on_user", "completed", "failed"]
    phase_id: str
    row: str
    session_id: str
    opaque_state: dict[str, Any]
    tool_result: dict
    blocked_reason: Optional[str]
    resume_token: Optional[str]


def _continuation_id(session_id: str, phase_id: str) -> str:
    return f"continuation:{session_id}:{phase_id}"


def persist(envelope: PhaseStateEnvelope) -> str:
    """Upsert a ``Continuation`` node carrying the full envelope.

    Returns the node id so callers can log it. Spec 07-v1 §FR4.
    """
    from context import get_store  # late import — avoids circular at module load

    store = get_store()
    node_id = _continuation_id(envelope["session_id"], envelope["phase_id"])
    store.upsert_node(
        node_id,
        {
            "id": node_id,
            "session_id": envelope["session_id"],
            "phase_id": envelope["phase_id"],
            "opaque_state": envelope["opaque_state"],
            "envelope": envelope,
            "created_at_epoch": int(time.time()),
        },
        label="Continuation",
    )
    return node_id


def hydrate(session_id: str, phase_id: str) -> Optional[PhaseStateEnvelope]:
    """Read a previously-persisted Continuation. Returns None on miss."""
    from context import get_store

    store = get_store()
    node_id = _continuation_id(session_id, phase_id)
    rows = store.query(
        "MATCH (c:Continuation {id: $id}) RETURN c",
        params={"id": node_id},
    )
    if not rows:
        return None
    row = rows[0]
    # GraphQLite returns dicts with a "properties" sub-key; the raw-SQLite
    # fallback (still present until spec 08-v1's StoreUnavailable lands) emits
    # rows shaped like `{id, type, payload}`. Tolerate both for the v0.1
    # transition period.
    c = row.get("c", row)
    if isinstance(c, dict):
        props = c.get("properties") or c.get("payload") or c
        if isinstance(props, str):
            import json
            try:
                props = json.loads(props)
            except Exception:
                return None
        return props.get("envelope") if isinstance(props, dict) else None
    return None


def delete(session_id: str, phase_id: str) -> None:
    """Remove the Continuation node, e.g. after a terminal status."""
    from context import get_store

    store = get_store()
    node_id = _continuation_id(session_id, phase_id)
    store.query(
        "MATCH (c:Continuation {id: $id}) DELETE c",
        params={"id": node_id},
    )


def sweep_ttl() -> None:
    """Delete Continuation nodes older than 30 days.

    Best-effort: a per-delete failure logs a warning but does NOT abort.
    Spec 07-v1 §FR7.
    """
    from context import get_store

    cutoff = int(time.time()) - THIRTY_DAYS_S
    try:
        store = get_store()
    except Exception as exc:  # pragma: no cover — Store boot failure
        logger.warning("ttl_sweep skipped — store unavailable: %s", exc)
        return

    try:
        expired = store.query(
            "MATCH (c:Continuation) WHERE c.created_at_epoch < $cutoff RETURN c",
            params={"cutoff": cutoff},
        )
    except Exception as exc:  # pragma: no cover — empty graph / driver edge case
        logger.warning("ttl_sweep query failed: %s", exc)
        return

    for row in expired or []:
        c = row.get("c", row) if isinstance(row, dict) else None
        if not isinstance(c, dict):
            continue
        props = c.get("properties") or c.get("payload") or c
        if isinstance(props, str):
            import json
            try:
                props = json.loads(props)
            except Exception:
                continue
        cid = props.get("id") if isinstance(props, dict) else None
        if not cid:
            continue
        try:
            store.query(
                "MATCH (c:Continuation {id: $id}) DELETE c",
                params={"id": cid},
            )
            logger.info("ttl_sweep deleted continuation=%s", cid)
        except Exception as exc:
            logger.warning("ttl_sweep delete failed for %s: %s", cid, exc)
