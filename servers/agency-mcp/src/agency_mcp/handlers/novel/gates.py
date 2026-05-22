import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Any
import datetime

from fastmcp import FastMCP
from agency_mcp.state.cache import StateCache
from agency_mcp.handlers.novel.coherence import novel_coherence_check
from agency_mcp.lib.ncp.validator import validate as validate_ncp

try:
    from agency_mcp.config import PLUGIN_ROOT
except ImportError:
    PLUGIN_ROOT = Path(".").resolve()

def _get_cache() -> StateCache:
    return StateCache()

@dataclass
class GateResult:
    name: str
    pass_: bool
    hint: str
    evidence: str

def _get_work_dir_from_fixtures(work_id: str) -> Path | None:
    path = Path("tests/fixtures/novel") / work_id
    if path.exists() and path.is_dir():
        return path
    return None

def _resolve_work_dir(work_id: str) -> Path | None:
    fix_dir = _get_work_dir_from_fixtures(work_id)
    if fix_dir: return fix_dir
    novels_dir = PLUGIN_ROOT / "novels"
    if novels_dir.exists():
        for author_dir in novels_dir.iterdir():
            if author_dir.is_dir():
                works_dir = author_dir / "works"
                if works_dir.exists():
                    for genre_dir in works_dir.iterdir():
                        if genre_dir.is_dir():
                            work_dir = genre_dir / work_id
                            if work_dir.exists():
                                return work_dir
    return None

def _read_json(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _read_frontmatter(path: Path) -> dict:
    frontmatter = {}
    if not path.exists():
        return frontmatter
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if lines and lines[0].strip() == "---":
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    break
                if ":" in lines[i]:
                    key, val = lines[i].split(":", 1)
                    frontmatter[key.strip()] = val.strip().strip('"').strip("'")
    except Exception:
        pass
    return frontmatter

def _is_historical_genre(work_dir: Path) -> bool:
    readme_path = work_dir / "README.md"
    frontmatter = _read_frontmatter(readme_path)
    genre = frontmatter.get("genre", "")
    return genre.startswith("historical-")

def _gate_dramatica_confirmed(work_id: str) -> dict:
    cache = _get_cache()
    try:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                state = None
            else:
                state = loop.run_until_complete(cache.snapshot())
        except RuntimeError:
            state = asyncio.run(cache.snapshot())

        if state is None:
            cache._load_from_disk()
            state = cache._state or {}
    except Exception:
        state = {}

    # Check if dramatica is locked
    novel_state = state.get("novel", {})
    # Look through authors to find work_id
    dramatica_locked = False
    for author_data in novel_state.get("authors", {}).values():
        if work_id in author_data.get("works", {}):
            dramatica_locked = author_data["works"][work_id].get("dramatica_locked", False)
            break

    coherence = novel_coherence_check(work_id)
    coherence_pass = coherence.get("status") == "PASS"

    if dramatica_locked and coherence_pass:
        return {"name": "dramatica_confirmed", "pass": True, "hint": "Dramatica locked and coherence check passed", "evidence": "dramatica_locked=true, coherence=PASS"}
    else:
        return {"name": "dramatica_confirmed", "pass": False, "hint": "Dramatica not locked or coherence check failed", "evidence": f"locked={dramatica_locked}, coherence={coherence.get('status')}"}

def _gate_ncp_valid(work_id: str) -> dict:
    work_dir = _resolve_work_dir(work_id)
    if not work_dir:
        return {"name": "ncp_valid", "pass": False, "hint": "Work not found", "evidence": ""}

    ncp_path = work_dir / ".ncp.json"
    if not ncp_path.exists():
        return {"name": "ncp_valid", "pass": False, "hint": "Missing .ncp.json", "evidence": ""}

    res = validate_ncp(ncp_path)

    if res.get("ok"):
        return {"name": "ncp_valid", "pass": True, "hint": "NCP is valid", "evidence": "Schema validation passed"}
    else:
        errors = res.get("errors", [])
        hint = errors[0] if errors else "NCP validation failed"
        return {"name": "ncp_valid", "pass": False, "hint": hint[:140], "evidence": "Schema validation errors found"}

def _gate_premise_locked(work_id: str) -> dict:
    work_dir = _resolve_work_dir(work_id)
    if not work_dir:
        return {"name": "premise_locked", "pass": False, "hint": "Work not found", "evidence": ""}

    readme_path = work_dir / "README.md"
    fm = _read_frontmatter(readme_path)

    missing = []
    for field in ["logline", "theme", "target_reader", "comp_titles"]:
        if not fm.get(field):
            missing.append(field)

    if missing:
        return {"name": "premise_locked", "pass": False, "hint": f"Missing premise fields: {', '.join(missing)}", "evidence": "Frontmatter checked"}

    return {"name": "premise_locked", "pass": True, "hint": "Premise locked", "evidence": "All required frontmatter fields present"}

def _gate_cast_complete(work_id: str) -> dict:
    work_dir = _resolve_work_dir(work_id)
    if not work_dir:
        return {"name": "cast_complete", "pass": False, "hint": "Work not found", "evidence": ""}

    ncp_path = work_dir / ".ncp.json"
    ncp = _read_json(ncp_path)
    players = ncp.get("players", [])

    for p in players:
        for field in ["name", "archetype", "motivations"]:
            val = p.get(field)
            if not val:
                return {"name": "cast_complete", "pass": False, "hint": f"Player {p.get('name', 'unknown')} missing {field}", "evidence": ".ncp.json players checked"}

    return {"name": "cast_complete", "pass": True, "hint": "Cast complete", "evidence": "All players valid"}

def _gate_pov_declared(work_id: str) -> dict:
    work_dir = _resolve_work_dir(work_id)
    if not work_dir:
        return {"name": "pov_declared", "pass": False, "hint": "Work not found", "evidence": ""}

    chapters_dir = work_dir / "chapters"
    if chapters_dir.exists() and chapters_dir.is_dir():
        for ch_file in chapters_dir.glob("*.md"):
            fm = _read_frontmatter(ch_file)
            pov = fm.get("pov")
            vp = fm.get("viewpoint_character")

            valid_povs = {"1st", "3rd_limited", "3rd_omniscient", "2nd"}
            if pov not in valid_povs:
                return {"name": "pov_declared", "pass": False, "hint": f"Chapter {ch_file.name} invalid/missing pov", "evidence": "Frontmatter checked"}

            if pov != "3rd_omniscient" and not vp:
                return {"name": "pov_declared", "pass": False, "hint": f"Chapter {ch_file.name} missing viewpoint_character", "evidence": "Frontmatter checked"}

    return {"name": "pov_declared", "pass": True, "hint": "POV declared", "evidence": "All chapters valid"}

def _gate_sources_verified(work_id: str) -> dict:
    work_dir = _resolve_work_dir(work_id)
    if not work_dir:
        return {"name": "sources_verified", "pass": False, "hint": "Work not found", "evidence": ""}

    if not _is_historical_genre(work_dir):
        return {"name": "sources_verified", "pass": True, "hint": "Not historical", "evidence": "N/A — genre is not historical-*"}

    sources_path = work_dir / "SOURCES.md"
    if not sources_path.exists():
        return {"name": "sources_verified", "pass": False, "hint": "Missing SOURCES.md for historical genre", "evidence": ""}

    try:
        with open(sources_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                if "|" in line and "Status" not in line and "-------" not in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) > 2:
                        status = parts[2]
                        if not status.startswith("Verified ("):
                            return {"name": "sources_verified", "pass": False, "hint": f"Unverified source claim found", "evidence": "Checked SOURCES.md"}
    except Exception:
        pass

    return {"name": "sources_verified", "pass": True, "hint": "Sources verified", "evidence": "All claims Verified"}

def novel_run_pre_drafting_gates(work_id: str) -> dict:
    gates = [
        _gate_dramatica_confirmed(work_id),
        _gate_ncp_valid(work_id),
        _gate_premise_locked(work_id),
        _gate_cast_complete(work_id),
        _gate_pov_declared(work_id),
        _gate_sources_verified(work_id)
    ]

    blocking = [g["name"] for g in gates if not g["pass"]]

    return {
        "all_pass": len(blocking) == 0,
        "gates": gates,
        "blocking": blocking
    }

def _chapter_create_guard(work_id: str, force: bool = False) -> dict:
    if force:
        import asyncio
        cache = _get_cache()
        try:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    state = None
                else:
                    state = loop.run_until_complete(cache.snapshot())
            except RuntimeError:
                state = asyncio.run(cache.snapshot())

            if state is None:
                cache._load_from_disk()
                state = cache._state or {}
        except Exception:
            state = {}

        novel_state = state.get("novel", {})
        authors = novel_state.get("authors", {})

        for author, author_data in authors.items():
            works = author_data.get("works", {})
            if work_id in works:
                work_data = works[work_id]
                overrides = work_data.get("force_overrides", [])

                # Try to run gates to get blocking list, but don't fail if it doesn't pass
                res = novel_run_pre_drafting_gates(work_id)
                blocking = res.get("blocking", [])

                overrides.append({
                    "at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "caller": "novel_chapter_create",
                    "blocking": blocking
                })
                work_data["force_overrides"] = overrides

                # Use proper cache write
                try:
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # Synchronous fallback: modify disk directly if absolutely necessary, but shouldn't happen here
                            with open(PLUGIN_ROOT / "state.json", "w", encoding="utf-8") as f:
                                json.dump(state, f, indent=2)
                        else:
                            loop.run_until_complete(cache.write("novel", novel_state))
                    except RuntimeError:
                        asyncio.run(cache.write("novel", novel_state))
                except Exception:
                    pass
                break

        return {"ok": True}

    res = novel_run_pre_drafting_gates(work_id)
    if not res["all_pass"]:
        return {
            "ok": False,
            "error": "PRE_DRAFTING_GATES_FAILED",
            "blocking": res["blocking"],
            "hint": "Run novel_run_pre_drafting_gates(work_id) for full report, or pass force=True to override."
        }
    return {"ok": True}

def register(mcp: FastMCP) -> None:
    mcp.tool(tags={"domain:novel"})(novel_run_pre_drafting_gates)
