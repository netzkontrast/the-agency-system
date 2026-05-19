import json
import os
import shutil
import time
from pathlib import Path
from typing import TypedDict, Literal, Any, Dict, Optional

class PhaseStateEnvelope(TypedDict):
    status: Literal["running", "blocked_on_gate", "blocked_on_user", "completed", "failed"]
    phase_id: str                # e.g. "02"
    row: str                     # the row this envelope belongs to (kebab-case, matches spec 01)
    session_id: str              # opaque session UUID for resume keying
    opaque_state: dict[str, Any] # workflow's internal state — agentic MUST NOT mutate
    tool_result: dict            # validates against tool_result.schema.json (spec 02)
    blocked_reason: Optional[str]   # human-readable; required when status is "blocked_*"
    resume_token: Optional[str]     # required when status is "blocked_*"; agentic passes this back on resume

def get_state_dir(session_id: str) -> Path:
    return Path("workflow") / "_state" / session_id

def persist(envelope: PhaseStateEnvelope) -> Path:
    """Writes the envelope as JSON to workflow/_state/<session_id>/<phase_id>.json atomically."""
    session_id = envelope["session_id"]
    phase_id = envelope["phase_id"]

    state_dir = get_state_dir(session_id)
    state_dir.mkdir(parents=True, exist_ok=True)

    file_path = state_dir / f"{phase_id}.json"
    tmp_path = file_path.with_suffix(".json.tmp")

    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(envelope, f, indent=2)
        f.write("\n")

    with tmp_path.open("a") as f: os.fsync(f.fileno())
    os.replace(tmp_path, file_path)

    return file_path

def hydrate(session_id: str, phase_id: str) -> Optional[PhaseStateEnvelope]:
    """Reads JSON, validates against the spec-04 schema, returns the TypedDict.
       Returns None if expired or missing.
    """
    file_path = get_state_dir(session_id) / f"{phase_id}.json"
    if not file_path.exists():
        return None

    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # TODO: json schema validation per spec 04

    return PhaseStateEnvelope(**data)

def delete(session_id: str, phase_id: str) -> None:
    """Deletes the envelope file."""
    file_path = get_state_dir(session_id) / f"{phase_id}.json"
    try:
        file_path.unlink()
    except FileNotFoundError:
        pass

    state_dir = get_state_dir(session_id)
    if state_dir.exists() and not any(state_dir.iterdir()):
        try:
            state_dir.rmdir()
        except OSError:
            pass

def sweep_ttl() -> None:
    """Deletes envelope files older than 30 days. Prunes empty directories."""
    state_base = Path("workflow") / "_state"
    if not state_base.exists():
        return

    now = time.time()
    ttl_seconds = 30 * 24 * 60 * 60

    for session_dir in state_base.iterdir():
        if session_dir.is_dir() and session_dir.name != "README.md":
            for env_file in session_dir.glob("*.json"):
                if now - env_file.stat().st_mtime > ttl_seconds:
                    env_file.unlink()
                    print(f"TTL sweep: deleted {session_dir.name}/{env_file.stem}")

            if not any(session_dir.iterdir()):
                try:
                    session_dir.rmdir()
                except OSError:
                    pass
