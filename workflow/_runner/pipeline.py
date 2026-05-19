import uuid
from typing import Dict, Any, List
import jinja2
from pathlib import Path
from workflow._runner.envelope import PhaseStateEnvelope, persist, hydrate, delete, sweep_ttl
from context import Store

def boot() -> None:
    sweep_ttl()

def start(row: str, phase_id: str, inputs: Dict[str, Any], lazy_link: bool = False) -> PhaseStateEnvelope:
    """Entry point for mcp__<row>_start / scaffold"""
    session_id = str(uuid.uuid4())


    # Mock Phase node retrieval via context.query
    # In v1, the pipeline runner READS a Phase node from the graph.
    # We mock it here for the base layer.
    def _mock_query_phase(row_val, phase_val):
        if row_val == "meta":
            return {"body_ref": f"phases/{phase_val}.md"}
        return None

    phase_node = _mock_query_phase(row, phase_id)
    if not phase_node:
        if lazy_link:
            # Add a lazy_create_path operation (mock)
            # Create the missing phase as a placeholder node and continue
            phase_node = {"body_ref": f"phases/{phase_id}.md", "_lazy_created": True}
        else:
            return {
                "status": "failed",
                "phase_id": phase_id,
                "row": row,
                "session_id": session_id,
                "opaque_state": {},
                "tool_result": {
                    "ok": False,
                    "data": {"error": {"message": f"row {row} phase {phase_id} not found in graph. Use lazy_link=True to create."}},
                    "warnings": [],
                    "next_suggested_tools": []
                },
                "blocked_reason": None,
                "resume_token": None
            }

    if row == "meta":
        return _run_meta_scaffold(session_id, inputs)

    # placeholder for actual pipeline runner logic for other rows
    return {
        "status": "failed",
        "phase_id": phase_id,
        "row": row,
        "session_id": session_id,
        "opaque_state": {},
        "tool_result": {
            "ok": False,
            "data": {"error": {"message": f"row {row} not supported in base pipeline"}},
            "warnings": [],
            "next_suggested_tools": []
        },
        "blocked_reason": None,
        "resume_token": None
    }

def resume(session_id: str, phase_id: str, user_response: Any) -> PhaseStateEnvelope:
    env = hydrate(session_id, phase_id)
    if not env:
        return {
            "status": "failed",
            "phase_id": phase_id,
            "row": "unknown", # can't know without hydrate
            "session_id": session_id,
            "opaque_state": {},
            "tool_result": {
                "ok": False,
                "data": {"error": {"code": "RESUME_EXPIRED"}},
                "warnings": [],
                "next_suggested_tools": []
            },
            "blocked_reason": None,
            "resume_token": None
        }

    if env["status"] in ["completed", "failed"]:
        # terminal
        env["tool_result"]["ok"] = False
        env["tool_result"]["data"] = {"error": {"code": "RESUME_TERMINAL"}}
        return env

    # merge response and continue (mock logic for now)
    env["status"] = "running"
    if isinstance(user_response, dict):
        env["opaque_state"].update(user_response)

    return env

def _run_meta_scaffold(session_id: str, inputs: Dict[str, Any]) -> PhaseStateEnvelope:
    new_row = inputs.get("new_row", "")

    # 01-bootstrap (spec 01)
    import re
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
                "next_suggested_tools": []
            },
            "blocked_reason": "row name invalid",
            "resume_token": "rt_meta_01"
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
                    "next_suggested_tools": []
                },
                "blocked_reason": "row already exists",
                "resume_token": "rt_meta_01"
            }

    # 02-scaffold
    created_cells = []
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

        # W5: emit a Cell node per column so the scaffolded cell is
        # discoverable in the graph, not just on disk.
        g.upsert_node(
            f"cell/{col}/{new_row}",
            {
                "row": new_row,
                "column": col,
                "manifest_path": str(manifest_path),
            },
            label="Cell",
        )

    # W5: emit the Row node and a Phase node for the scaffold step, plus a
    # PRECEDES edge so the meta workflow's two phases are linked in the graph.
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
                "created_cells": created_cells
            },
            "warnings": [],
            "next_suggested_tools": [f"mcp__{new_row}_scaffold"]
        },
        "blocked_reason": None,
        "resume_token": None
    }
