"""Workflow pipeline entry-points.

Spec 07-v1 §FR3 — ``start`` is now a generic graph walker. Non-meta rows
go through :func:`_walk_phase`, which resolves the row's MCP handler
from the agentic cell registry, evaluates blocking gates, reads the
phase prose body, and invokes the handler.

The ``meta`` row preserves its v0 scaffolder contract (PR #150 + PR
#155 W5). The meta-scaffolder continues to use ``from context import
Store`` so the existing ``tests/workflow/test_meta_scaffold.py``
monkeypatches stay valid.
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import jinja2

from context import Store, get_store
from context._shared import error_codes
from workflow._runner import manifest as manifest_reader
from workflow._runner.envelope import (
    PhaseStateEnvelope,
    delete as envelope_delete,
    hydrate,
    persist,
    sweep_ttl,
)
from workflow._runner.gate import evaluate_gate

# Cached handler registry — populated lazily on first walker call.
# Spec 07-v1 §FR3: "cached at boot" via `agentic._harness.cell_loader.discover`.
_HANDLER_REGISTRY = None


def _get_handler_registry():
    """Return the agentic cell registry, building it once per process."""
    global _HANDLER_REGISTRY
    if _HANDLER_REGISTRY is None:
        from agentic._harness.cell_loader import discover

        _HANDLER_REGISTRY = discover(Path("."))
    return _HANDLER_REGISTRY


def _reset_handler_registry_for_tests() -> None:
    """Test-only helper — clear the cached registry."""
    global _HANDLER_REGISTRY
    _HANDLER_REGISTRY = None


def boot() -> None:
    """Pipeline boot: Continuation TTL sweep + Phase-node seeding for
    hand-rolled rows.

    The meta-row scaffolder materialises Phase nodes for any row it creates,
    but rows that were authored directly on disk (like the `jules` row in
    v0.1) have a manifest + phase MDs but no graph nodes until something
    seeds them. Walking `workflow/<row>/phases/*.md` once at boot keeps the
    walker reachable without forcing a separate seed command.
    """
    sweep_ttl()
    _seed_phase_nodes_for_hand_rolled_rows()


def _parse_phase_frontmatter(md_path: Path) -> Dict[str, Any]:
    """Read YAML frontmatter from a phase MD. Tolerates missing frontmatter."""
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    import yaml as _yaml
    try:
        meta = _yaml.safe_load(text[3:end]) or {}
    except Exception:
        return {}
    return meta if isinstance(meta, dict) else {}


def _seed_phase_nodes_for_hand_rolled_rows() -> None:
    """Upsert Phase nodes for every workflow/<row>/phases/*.md.

    Idempotent — `upsert_node` is a write-or-replace. The meta row is
    skipped because its phases are materialised dynamically by the
    scaffolder for each new target row. Phase id is the leading digits of
    the MD filename; the rest of the filename is descriptive.
    """
    workflow_dir = Path("workflow")
    if not workflow_dir.exists():
        return
    g = get_store()
    for row_dir in workflow_dir.iterdir():
        if not row_dir.is_dir() or row_dir.name.startswith("_"):
            continue
        if row_dir.name == "meta":
            continue
        phases_dir = row_dir / "phases"
        if not phases_dir.is_dir():
            continue
        for md in sorted(phases_dir.glob("*.md")):
            m = re.match(r"^(\d+)", md.stem)
            if not m:
                continue
            phase_id = m.group(1)
            meta = _parse_phase_frontmatter(md)
            payload = {
                "row": row_dir.name,
                "phase_id": phase_id,
                "body_ref": f"phases/{md.name}",
                "lazy_created": False,
            }
            if "entry_verb" in meta:
                payload["entry_verb"] = meta["entry_verb"]
            if "description" in meta:
                payload["description"] = meta["description"]
            g.upsert_node(
                f"phase/{row_dir.name}/{phase_id}",
                payload,
                label="Phase",
            )


# ---------------------------------------------------------------------------
# Envelope builders
# ---------------------------------------------------------------------------

def _failed_envelope(
    session_id: str,
    row: str,
    phase_id: str,
    message: str,
    *,
    code: Optional[str] = None,
) -> PhaseStateEnvelope:
    error: Dict[str, Any] = {"message": message}
    if code:
        error["code"] = code
    return {
        "status": "failed",
        "phase_id": phase_id,
        "row": row,
        "session_id": session_id,
        "opaque_state": {},
        "tool_result": {
            "ok": False,
            "data": {"error": error},
            "warnings": [],
            "next_suggested_tools": [],
        },
        "blocked_reason": None,
        "resume_token": None,
    }


def _blocked_on_gate_envelope(
    session_id: str,
    row: str,
    phase_id: str,
    message: str,
) -> PhaseStateEnvelope:
    return {
        "status": "blocked_on_gate",
        "phase_id": phase_id,
        "row": row,
        "session_id": session_id,
        "opaque_state": {},
        "tool_result": {
            "ok": False,
            "data": {"error": {"message": message}},
            "warnings": [],
            "next_suggested_tools": [],
        },
        "blocked_reason": message,
        "resume_token": None,
    }


# ---------------------------------------------------------------------------
# Phase node access
# ---------------------------------------------------------------------------

def _phase_node(g, row: str, phase_id: str) -> Optional[Dict[str, Any]]:
    """Look up the Phase node payload for (row, phase_id).

    Tolerates GraphQLite's ``{"p": {"properties": {...}}}`` shape AND
    the raw-SQLite fallback's ``{"p": {"payload": "..."}}`` shape — the
    latter persists until spec 08-v1 deletes the fallback.
    """
    rows = g.query(
        "MATCH (p:Phase {row: $row, phase_id: $pid}) RETURN p",
        params={"row": row, "pid": phase_id},
    )
    if not rows:
        return None
    p = rows[0].get("p", rows[0]) if isinstance(rows[0], dict) else None
    if not isinstance(p, dict):
        return None
    props = p.get("properties") or p.get("payload") or p
    if isinstance(props, str):
        import json
        try:
            props = json.loads(props)
        except Exception:
            return None
    return props if isinstance(props, dict) else None


def _lazy_create_phase(g, row: str, phase_id: str, session_id: str) -> Dict[str, Any]:
    """Upsert a placeholder Phase node and return its payload."""
    payload = {
        "row": row,
        "phase_id": phase_id,
        "body_ref": f"phases/{phase_id}.md",
        "lazy_created": True,
        "scaffolded_by": session_id,
    }
    g.upsert_node(f"phase/{row}/{phase_id}", payload, label="Phase")
    return payload


# ---------------------------------------------------------------------------
# Public verbs
# ---------------------------------------------------------------------------

def start(
    row: str,
    phase_id: str,
    inputs: Dict[str, Any],
    lazy_link: bool = False,
) -> PhaseStateEnvelope:
    """Entry-point for ``mcp__<row>_start`` (and ``mcp__meta_scaffold``).

    Spec 07-v1 §FR3 — generic graph walker.
    """
    session_id = str(uuid.uuid4())

    # The meta-row is the bootstrap that materialises every other row's
    # Phase nodes — querying the graph for `phase/meta/01` before it has
    # ever run is a chicken-and-egg. Spec 07-v1 §FR5 keeps the meta-row
    # scaffolder on its v0 contract; short-circuit before the graph
    # lookup so the bootstrap remains callable on a fresh ontology.
    if row == "meta":
        return _run_meta_scaffold(session_id, inputs)

    # Honor the row's opt-out even when the caller asks for lazy-link.
    if lazy_link and not manifest_reader.get_lazy_link(row):
        return _failed_envelope(
            session_id,
            row,
            phase_id,
            (
                f"row {row} has [workflow.lazy_link] enabled = false; "
                f"caller's lazy_link=True ignored"
            ),
        )

    g = get_store()

    phase_node = _phase_node(g, row, phase_id)
    if phase_node is None:
        if not lazy_link:
            # Message contains both "not in graph" (spec 07-v1) and
            # "not found in graph" (legacy test_pipeline.py phrasing).
            return _failed_envelope(
                session_id,
                row,
                phase_id,
                (
                    f"row {row} phase {phase_id} not in graph "
                    f"(not found in graph). Use lazy_link=True to create."
                ),
            )
        phase_node = _lazy_create_phase(g, row, phase_id, session_id)

    return _walk_phase(session_id, row, phase_id, phase_node, inputs)


def resume(
    session_id: str,
    phase_id: str,
    user_response: Any,
) -> PhaseStateEnvelope:
    """Hydrate a Continuation, merge ``user_response``, re-walk the phase.

    Spec 07-v1 §FR4: shallow-merge ``user_response`` into ``opaque_state``,
    re-walk the phase via :func:`_walk_phase`, and on terminal status
    (``completed`` / ``failed``) delete the Continuation node.
    """
    env = hydrate(session_id, phase_id)
    if not env:
        return {
            "status": "failed",
            "phase_id": phase_id,
            "row": "unknown",
            "session_id": session_id,
            "opaque_state": {},
            "tool_result": {
                "ok": False,
                "data": {"error": {"code": error_codes.RESUME_EXPIRED}},
                "warnings": [],
                "next_suggested_tools": [],
            },
            "blocked_reason": None,
            "resume_token": None,
        }

    if env["status"] in ("completed", "failed"):
        env["tool_result"]["ok"] = False
        env["tool_result"]["data"] = {"error": {"code": error_codes.RESUME_TERMINAL}}
        return env

    # Shallow merge of user_response into opaque_state (spec 07-v1 §FR4:
    # top-level keys in user_response overwrite top-level keys in
    # opaque_state; nested merging is out of scope).
    if isinstance(user_response, dict):
        env["opaque_state"].update(user_response)

    row = env["row"]

    # Re-walk the phase. The phase node must still exist in the graph —
    # if it doesn't, the row was scaffolded away under us and we surface
    # that as a failure rather than silently dropping the resume.
    g = get_store()
    phase_node = _phase_node(g, row, phase_id)
    if phase_node is None:
        envelope_delete(session_id, phase_id)
        return _failed_envelope(
            session_id,
            row,
            phase_id,
            f"row {row} phase {phase_id} not in graph on resume",
            code=error_codes.RESUME_PHASE_GONE,
        )

    new_env = _walk_phase(session_id, row, phase_id, phase_node, env["opaque_state"])
    # Preserve the original session_id across the re-walk (`_walk_phase`
    # doesn't mint a new one, but be explicit).
    new_env["session_id"] = session_id

    # Terminal status clears the Continuation node. A `blocked_on_user`
    # outcome means `_walk_phase` already re-persisted the envelope, so
    # leave it in place.
    if new_env["status"] in ("completed", "failed"):
        envelope_delete(session_id, phase_id)

    return new_env


# ---------------------------------------------------------------------------
# Generic graph walker
# ---------------------------------------------------------------------------

def _resolve_handler(row: str, entry_verb: str) -> Optional[Callable[..., dict]]:
    """Return the registered ``mcp__<row>_<verb>`` callable, or None."""
    registry = _get_handler_registry()
    tool_name = f"mcp__{row}_{entry_verb}"
    return registry.tools.get(tool_name)


def _read_phase_body(row: str, body_ref: str) -> Optional[str]:
    path = Path(f"workflow/{row}") / body_ref
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(body: str) -> Dict[str, Any]:
    """Pull the YAML frontmatter from a Markdown phase body, if any."""
    match = _FRONTMATTER_RE.match(body)
    if not match:
        return {}
    try:
        import yaml

        data = yaml.safe_load(match.group(1)) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _collect_blocking_gates(row: str, phase_id: str) -> List[Path]:
    """Find all gate YAML files that BLOCK this phase.

    v0.1 is disk-only: scans ``workflow/<row>/gates/*.yaml`` filtered by
    ``blocks_phase``. Graph-edge gate discovery
    (``(p:Phase)<-[:BLOCKS]-(g:Gate)``) is post-v0.1, deferred until the
    gate evaluator seeds ``BLOCKS`` edges into the ontology.
    """
    gates_dir = Path(f"workflow/{row}/gates")
    if not gates_dir.exists():
        return []
    import yaml as _yaml

    out: List[Path] = []
    for yp in sorted(gates_dir.glob("*.yaml")):
        try:
            data = _yaml.safe_load(yp.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        if str(data.get("blocks_phase", "")) == str(phase_id):
            out.append(yp)
    return out


def _walk_phase(
    session_id: str,
    row: str,
    phase_id: str,
    phase_node: Dict[str, Any],
    inputs: Dict[str, Any],
) -> PhaseStateEnvelope:
    """Execute a single Phase node. Spec 07-v1 §FR3 ``_walk_phase`` contract."""
    body_ref = phase_node.get("body_ref") or f"phases/{phase_id}.md"

    # 1 — read the prose body. Body presence determines the entry_verb
    # (frontmatter override) so we read it before resolving the handler.
    body = _read_phase_body(row, body_ref)
    if body is None:
        resolved = str(Path(f"workflow/{row}") / body_ref)
        env = _failed_envelope(
            session_id, row, phase_id,
            f"phase body not found at {resolved}",
            code=error_codes.PHASE_BODY_MISSING,
        )
        return env

    frontmatter = _parse_frontmatter(body)
    entry_verb = frontmatter.get("entry_verb", "start")

    # 2 — resolve handler.
    handler = _resolve_handler(row, entry_verb)
    if handler is None:
        env = _failed_envelope(
            session_id, row, phase_id,
            f"no MCP tool registered for mcp__{row}_{entry_verb}",
            code=error_codes.HANDLER_NOT_FOUND,
        )
        return env

    # 3 — gate evaluation in declaration order. First hard-blocking
    # failure short-circuits; advisory failures collect into warnings.
    warnings: List[str] = []
    import yaml as _yaml

    for gate_path in _collect_blocking_gates(row, phase_id):
        try:
            gate_def = _yaml.safe_load(gate_path.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        ok, message, _emitted = evaluate_gate(gate_path, {"row": row, "phase_id": phase_id, "inputs": inputs})
        if ok:
            continue
        gate_type = gate_def.get("type", "hard-blocking")
        if gate_type == "hard-blocking":
            # Prefer the gate's on_failure.message when set; else evaluator msg.
            on_failure = gate_def.get("on_failure", {}) or {}
            block_msg = on_failure.get("message", message)
            return _blocked_on_gate_envelope(session_id, row, phase_id, block_msg)
        else:
            warnings.append(f"advisory gate {gate_def.get('id', gate_path.name)}: {message}")

    # 4 — invoke the handler.
    try:
        tool_result = handler(**inputs)
    except TypeError:
        # Handler signature mismatch — surface as failed envelope.
        tool_result = {
            "ok": False,
            "data": {"error": {"code": error_codes.HANDLER_BAD_SIGNATURE,
                               "message": f"handler mcp__{row}_{entry_verb} rejected inputs"}},
            "warnings": [],
            "next_suggested_tools": [],
        }
    except Exception as exc:
        tool_result = {
            "ok": False,
            "data": {"error": {"code": error_codes.HANDLER_EXCEPTION, "message": repr(exc)}},
            "warnings": [],
            "next_suggested_tools": [],
        }

    if not isinstance(tool_result, dict):
        tool_result = {
            "ok": False,
            "data": {"error": {"code": error_codes.HANDLER_BAD_RETURN,
                               "message": "handler did not return a dict"}},
            "warnings": [],
            "next_suggested_tools": [],
        }

    # Merge advisory gate warnings into the tool_result.
    if warnings:
        tool_result.setdefault("warnings", []).extend(warnings)

    # 5 — wrap as PhaseStateEnvelope.
    ok = bool(tool_result.get("ok"))
    status = "completed" if ok else "failed"
    envelope: PhaseStateEnvelope = {
        "status": status,
        "phase_id": phase_id,
        "row": row,
        "session_id": session_id,
        "opaque_state": dict(inputs) if isinstance(inputs, dict) else {},
        "tool_result": tool_result,
        "blocked_reason": None,
        "resume_token": None,
    }

    # 6 — Persist on blocked_on_user (handler can signal this).
    if tool_result.get("data", {}).get("blocked_on_user") is True:
        envelope["status"] = "blocked_on_user"
        envelope["blocked_reason"] = tool_result["data"].get("blocked_reason")
        envelope["resume_token"] = tool_result["data"].get("resume_token")
        persist(envelope)

    return envelope


# ---------------------------------------------------------------------------
# Meta-row scaffolder (unchanged from PR #150 + PR #155 W5)
# ---------------------------------------------------------------------------

def _run_meta_scaffold(session_id: str, inputs: Dict[str, Any]) -> PhaseStateEnvelope:
    new_row = inputs.get("new_row", "")

    # 01-bootstrap (spec 01)
    if not re.match(r"^[a-z][a-z0-9-]{0,30}$", new_row):
        return {
            "status": "blocked_on_user",
            "phase_id": "01",
            "row": "meta",
            "session_id": session_id,
            "opaque_state": {},
            "tool_result": {
                "ok": False,
                "data": {"error": {"fix_hint": "row name invalid"}},
                "warnings": [],
                "next_suggested_tools": [],
            },
            "blocked_reason": "row name invalid",
            "resume_token": "rt_meta_01",
        }

    for d in ["agentic", "workflow", "context"]:
        if (Path(d) / new_row).exists():
            return {
                "status": "blocked_on_user",
                "phase_id": "01",
                "row": "meta",
                "session_id": session_id,
                "opaque_state": {},
                "tool_result": {
                    "ok": False,
                    "data": {"error": {"fix_hint": "row already exists; delete or pick a different name"}},
                    "warnings": [],
                    "next_suggested_tools": [],
                },
                "blocked_reason": "row already exists",
                "resume_token": "rt_meta_01",
            }

    # 02-scaffold
    created_cells: List[str] = []
    template_dir = Path("workflow/meta/templates")
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)

    g = Store()
    g.boot()

    for col in ["agentic", "workflow", "context"]:
        out_dir = Path(f"{col}/{new_row}")
        out_dir.mkdir(parents=True, exist_ok=False)

        template = env.get_template(f"{col}-cell.toml.jinja")
        rendered = template.render(new_row=new_row)

        manifest_path = out_dir / "manifest.toml"
        manifest_path.write_text(rendered)
        created_cells.append(str(manifest_path))

        if col == "agentic":
            (out_dir / "skills").mkdir()
            (out_dir / "skills" / ".gitkeep").touch()
            (out_dir / "tools").mkdir()
            (out_dir / "tools" / ".gitkeep").touch()
        elif col == "workflow":
            (out_dir / "phases").mkdir()
            (out_dir / "phases" / ".gitkeep").touch()
            (out_dir / "gates").mkdir()
            (out_dir / "gates" / ".gitkeep").touch()
        elif col == "context":
            (out_dir / "schemas").mkdir()
            (out_dir / "schemas" / ".gitkeep").touch()
            (out_dir / "templates").mkdir()
            (out_dir / "templates" / ".gitkeep").touch()

        g.upsert_node(
            f"cell/{col}/{new_row}",
            {
                "row": new_row,
                "column": col,
                "manifest_path": str(manifest_path),
            },
            label="Cell",
        )

    g.upsert_node(
        f"row/{new_row}",
        {"row": new_row, "scaffolded_by": session_id},
        label="Row",
    )
    g.upsert_node(
        f"phase/meta/02:{new_row}",
        {"row": "meta", "phase_id": "02", "target_row": new_row},
        label="Phase",
    )
    g.upsert_edge(
        "phase/meta/01",
        f"phase/meta/02:{new_row}",
        {},
        rel_type="PRECEDES",
    )

    return {
        "status": "completed",
        "phase_id": "02",
        "row": "meta",
        "session_id": session_id,
        "opaque_state": {},
        "tool_result": {
            "ok": True,
            "data": {
                "created_cells": created_cells,
            },
            "warnings": [],
            "next_suggested_tools": [f"mcp__{new_row}_scaffold"],
        },
        "blocked_reason": None,
        "resume_token": None,
    }
