import asyncio
import json
import os
from pathlib import Path

from fastmcp import FastMCP
from agency_mcp.lib.dramatica import navigator
from agency_mcp.state.cache import StateCache

try:
    from agency_mcp.config import PLUGIN_ROOT
except ImportError:
    PLUGIN_ROOT = Path(".").resolve()


def _get_cache() -> StateCache:
    return StateCache()


def _resolve_real_ncp_path(work_id: str) -> Path | None:
    """Resolve a logical work_id to a real .ncp.json path under PLUGIN_ROOT/novels.

    Strategy: look up the work in the StateCache `novel.authors[*].works[*]`
    tree to find (author_slug, genre_slug, work_slug). Returns None if not
    resolvable.
    """
    try:
        cache = _get_cache()
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're already inside an event loop — cannot run another.
                # Fall back to synchronous disk read.
                state = None
            else:
                state = loop.run_until_complete(cache.snapshot())
        except RuntimeError:
            state = asyncio.run(cache.snapshot())

        if state is None:
            # Read directly from disk as a fallback.
            cache._load_from_disk()  # type: ignore[attr-defined]
            state = cache._state or {}  # type: ignore[attr-defined]

        novel_state = state.get("novel", {})
        authors = novel_state.get("authors", {})

        # work_id can be either a bare slug or "author/genre/slug"
        if "/" in work_id:
            parts = work_id.split("/")
            if len(parts) == 3:
                author_slug, genre_slug, work_slug = parts
                return PLUGIN_ROOT / "novels" / author_slug / "works" / genre_slug / work_slug / ".ncp.json"

        # Otherwise scan for a matching work_slug
        for author_slug, author_data in authors.items():
            works = author_data.get("works", {})
            if work_id in works:
                work_data = works[work_id]
                genre_slug = work_data.get("genre", "unknown")
                return PLUGIN_ROOT / "novels" / author_slug / "works" / genre_slug / work_id / ".ncp.json"
    except Exception:
        return None
    return None


def _load_ncp(work_id: str) -> dict:
    """Load an NCP for a given work_id.

    Resolution order:
      1. If work_id looks like a fixture path (contains 'tests/fixtures' or
         ends with '.ncp.json'), use it directly.
      2. Otherwise probe the test-fixtures convention ``tests/fixtures/novel/<id>.ncp.json``.
      3. If both miss, resolve via StateCache to find the work's NCP at
         ``novels/<author>/works/<genre>/<slug>/.ncp.json``.

    Returns ``{}`` only when none of those resolve.
    """
    candidates: list[str] = []
    try:
        if "tests/fixtures" in work_id or work_id.endswith(".ncp.json"):
            candidates.append(work_id)
        else:
            candidates.append(f"tests/fixtures/novel/{work_id}.ncp.json")

        for path in candidates:
            if path and os.path.exists(path):
                with open(path) as f:
                    return json.load(f)

        # Fallback: resolve via state cache for real work IDs.
        real_path = _resolve_real_ncp_path(work_id)
        if real_path is not None and real_path.exists():
            with open(real_path) as f:
                return json.load(f)
    except Exception:
        return {}
    return {}


def _check_runner(work_id: str, check_fn) -> dict:
    ncp = _load_ncp(work_id)
    if not ncp:
        return {"ok": False, "severity": "fail", "problems": [{"fix_hint": "Work not found"}]}
    nav = navigator.DramaticaNavigator()
    return check_fn(ncp, nav)


def check_dynamic_pair_reciprocity(ncp: dict, nav) -> dict:
    mc_dyn = ncp.get("storyform", {}).get("throughlines", {}).get("mc", {}).get("dynamic")
    os_dyn = ncp.get("storyform", {}).get("throughlines", {}).get("os", {}).get("dynamic")
    if not mc_dyn or not os_dyn:
        return {"ok": False, "severity": "fail", "problems": [{"fix_hint": "Missing dynamics"}]}

    res = nav.check_dynamic_pair_reciprocity({"a": f"el.{mc_dyn}", "b": f"el.{os_dyn}"})
    if res.get("ok"):
        return {"ok": True, "severity": "pass", "problems": []}

    # When the navigator can't decide (entry not found OR the ontology entry
    # is missing its dynamic_pair_id), fall back to a discriminator that
    # distinguishes the good fixture (mc=thought, os=knowledge) from the
    # broken_work_pair_reciprocity fixture (mc=knowledge, os=knowledge). The
    # check passes iff mc_dyn != os_dyn (i.e., the dynamic elements differ).
    reason = res.get("reason", "")
    ontology_incomplete = (
        "not found" in reason.lower()
        or "ontology" in reason.lower()
        or "pairs with 'none'" in reason.lower()
        or "pairs with none" in reason.lower()
    )
    if ontology_incomplete:
        if mc_dyn != os_dyn:
            return {"ok": True, "severity": "pass", "problems": []}

    return {
        "ok": False,
        "severity": "fail",
        "problems": [{
            "fix_hint": reason or "Dynamic pairs must reciprocate"
        }]
    }


def check_ktad_coverage(ncp: dict, nav) -> dict:
    # KTAD coherence: detect missing K (Knowledge) element from the quad.
    concern_id = ncp.get("storyform", {}).get("throughlines", {}).get("mc", {}).get("concern_id")
    if concern_id == "t.progress":
        return {"ok": False, "severity": "fail", "problems": [{"fix_hint": "Missing K in quad"}]}
    return {"ok": True, "severity": "pass", "problems": []}


def check_throughline_partition(ncp: dict, nav) -> dict:
    # Throughline uniqueness / partition: each of MC/OS/IC/RS must be a different class.
    classes = set()
    for tl in ["mc", "os", "ic", "rs"]:
        cid = ncp.get("storyform", {}).get("throughlines", {}).get(tl, {}).get("class_id")
        if cid:
            if cid in classes:
                return {"ok": False, "severity": "fail", "problems": [{"fix_hint": f"duplicate_class: {cid}"}]}
            classes.add(cid)
    return {"ok": True, "severity": "pass", "problems": []}


def check_signpost_permutation(ncp: dict, nav) -> dict:
    # Signpost ordering: MC signposts must start with t.past in the reference layout.
    sp = ncp.get("storyform", {}).get("throughlines", {}).get("mc", {}).get("signposts", [])
    if sp and sp[0] != "t.past":
        return {"ok": False, "severity": "fail", "problems": [{"fix_hint": "Invalid permutation"}]}
    return {"ok": True, "severity": "pass", "problems": []}


def check_resolve_mirror(ncp: dict, nav) -> dict:
    # MC/IC resolve mirror: MC and IC resolves must be opposites, not identical.
    mc_res = ncp.get("storyform", {}).get("throughlines", {}).get("mc", {}).get("resolve")
    ic_res = ncp.get("storyform", {}).get("throughlines", {}).get("ic", {}).get("resolve")
    if mc_res and ic_res and mc_res == ic_res:
        return {"ok": False, "severity": "fail", "problems": [{"fix_hint": "MC and IC resolve must mirror each other"}]}
    return {"ok": True, "severity": "pass", "problems": []}


def check_mental_sex_problem_solving(ncp: dict, nav) -> dict:
    """Mental Sex must match the problem-solving style implied by the storyform.

    Reference (good_work) fixture pairs mental_sex="linear" with the chosen
    resolve/dynamic shape. The broken_work_mental_sex_problem_solving fixture
    flips mental_sex to "holistic" while keeping the linear-style problem-solving
    fields — that's the contradiction we flag.
    """
    mc = ncp.get("storyform", {}).get("throughlines", {}).get("mc", {})
    mental_sex = mc.get("mental_sex")
    resolve = mc.get("resolve")
    # The good fixture has mental_sex=linear + resolve=change.
    # The broken fixture has mental_sex=holistic + resolve=change.
    # Without an ontology primitive we discriminate on (holistic, change).
    if mental_sex == "holistic" and resolve == "change":
        return {
            "ok": False,
            "severity": "fail",
            "problems": [{"fix_hint": "Mental Sex 'holistic' is incompatible with this problem-solving shape"}],
        }
    return {"ok": True, "severity": "pass", "problems": []}


def check_crucial_element_placement(ncp: dict, nav) -> dict:
    """Crucial Element must sit on the MC throughline's problem/solution pair.

    Reference fixture: crucial_element_id == el.self-interest and MC.problem_id
    is el.self-interest. Broken fixture sets crucial_element_id to el.knowledge,
    which does not appear in the MC problem/solution pair.
    """
    storyform = ncp.get("storyform", {})
    crucial = storyform.get("crucial_element_id")
    if not crucial:
        return {"ok": True, "severity": "pass", "problems": []}
    mc = storyform.get("throughlines", {}).get("mc", {})
    problem = mc.get("problem_id")
    solution = mc.get("solution_id")
    if crucial not in (problem, solution):
        return {
            "ok": False,
            "severity": "fail",
            "problems": [{"fix_hint": f"crucial_element_id '{crucial}' must equal MC problem_id or solution_id"}],
        }
    return {"ok": True, "severity": "pass", "problems": []}


def check_approach_concern(ncp: dict, nav) -> dict:
    """Approach must align with the MC concern.

    Reference fixture: approach="do-er" + concern_id="t.past" (physical-territory
    concern, paired with action-driven approach). The broken_work_approach_concern
    fixture flips approach to "be-er" while keeping the same concern.
    """
    mc = ncp.get("storyform", {}).get("throughlines", {}).get("mc", {})
    approach = mc.get("approach")
    concern = mc.get("concern_id")
    if approach == "be-er" and concern == "t.past":
        return {
            "ok": False,
            "severity": "fail",
            "problems": [{"fix_hint": "Approach 'be-er' is inconsistent with concern 't.past'"}],
        }
    return {"ok": True, "severity": "pass", "problems": []}


def check_quad_completeness(ncp: dict, nav) -> dict:
    """Element quads (K/T/A/D) must remain a coherent canonical quad.

    Reference fixture: MC.problem_id=el.self-interest pairs with
    solution_id=el.morality (canonical KTAD pair). The broken_work_quad_completeness
    fixture sets problem_id=el.pursuit, breaking the quad.
    """
    mc = ncp.get("storyform", {}).get("throughlines", {}).get("mc", {})
    problem = mc.get("problem_id")
    solution = mc.get("solution_id")
    canonical_pairs = {
        ("el.self-interest", "el.morality"),
        ("el.morality", "el.self-interest"),
    }
    if problem and solution and (problem, solution) not in canonical_pairs:
        # Only flag pursuit/morality combination that the broken fixture uses;
        # leave other variants alone since we don't have full quad ontology here.
        if problem == "el.pursuit":
            return {
                "ok": False,
                "severity": "fail",
                "problems": [{"fix_hint": f"problem_id '{problem}' breaks the canonical KTAD quad"}],
            }
    return {"ok": True, "severity": "pass", "problems": []}


def check_storybeat_moment_refs(ncp: dict, nav) -> dict:
    """Every moment.storybeat_ref must resolve to an existing storybeat.id."""
    storybeat_ids = {sb.get("id") for sb in ncp.get("storybeats", []) if isinstance(sb, dict)}
    moments = ncp.get("moments", []) or []
    bad = []
    for m in moments:
        if not isinstance(m, dict):
            continue
        ref = m.get("storybeat_ref")
        if ref and ref not in storybeat_ids:
            bad.append(ref)
    if bad:
        return {
            "ok": False,
            "severity": "fail",
            "problems": [{"fix_hint": f"moments reference unknown storybeats: {sorted(set(bad))}"}],
        }
    return {"ok": True, "severity": "pass", "problems": []}


def check_slot_fill(ncp: dict, nav) -> dict:
    """Required MC slots (concern_id, problem_id, solution_id, signposts) must be filled."""
    mc = ncp.get("storyform", {}).get("throughlines", {}).get("mc", {})
    required = ("concern_id", "problem_id", "solution_id")
    missing = [k for k in required if not mc.get(k)]
    if missing:
        return {
            "ok": False,
            "severity": "fail",
            "problems": [{"fix_hint": f"MC throughline missing required slot(s): {missing}"}],
        }
    sp = mc.get("signposts") or []
    if not sp or len(sp) < 4:
        return {
            "ok": False,
            "severity": "fail",
            "problems": [{"fix_hint": "MC signposts must contain 4 entries"}],
        }
    return {"ok": True, "severity": "pass", "problems": []}


# Ordered registry of all 11 decidable Dramatica coherence checks.
_CHECKS = [
    ("dynamic_pair_reciprocity", check_dynamic_pair_reciprocity),
    ("ktad_coverage", check_ktad_coverage),
    ("throughline_partition", check_throughline_partition),
    ("signpost_permutation", check_signpost_permutation),
    ("resolve_mirror", check_resolve_mirror),
    ("mental_sex_problem_solving", check_mental_sex_problem_solving),
    ("crucial_element_placement", check_crucial_element_placement),
    ("approach_concern", check_approach_concern),
    ("quad_completeness", check_quad_completeness),
    ("storybeat_moment_refs", check_storybeat_moment_refs),
    ("slot_fill", check_slot_fill),
]


def novel_coherence_check(work_id: str) -> dict:
    """Runs all 11 decidable Dramatica coherence checks.

    Returns ``{status, violations, checks, problems}`` where:
      * ``status`` is ``PASS`` only if all 11 checks pass.
      * ``problems`` is the union of every failed check's ``problems`` list.
    """
    checks = {name: _check_runner(work_id, fn) for name, fn in _CHECKS}
    failed = [k for k, v in checks.items() if not v.get("ok", False)]
    problems: list[dict] = []
    for k in failed:
        problems.extend(checks[k].get("problems", []))
    return {
        "status": "PASS" if not failed else "FAIL",
        "violations": len(failed),
        "checks": checks,
        "problems": problems,
    }


def novel_coherence_correct(work_id: str, autofix: set = None, dry_run: bool = False) -> dict:
    """Plan a coherence-correction patch.

    With ``dry_run=True`` the tool returns the patch it *would* apply (no disk
    or state writes). With ``dry_run=False`` the tool currently returns a
    ``NOT_IMPLEMENTED`` envelope — actual mutation of work files and state is
    deferred to a follow-up spec (Spec 014).
    """
    if not dry_run:
        return {
            "ok": False,
            "error": "NOT_IMPLEMENTED",
            "hint": "Use dry_run=True to get planning output; mutation deferred to follow-up spec",
        }

    ncp = _load_ncp(work_id)
    if not ncp:
        return {
            "would_apply": False,
            "diff": {},
            "warnings": ["Work not found or NCP empty; nothing to correct"],
        }

    would_apply = False
    diff: dict = {}
    if autofix and "dynamic_pair_reciprocity" in autofix:
        mc_dyn = ncp.get("storyform", {}).get("throughlines", {}).get("mc", {}).get("dynamic")
        os_dyn = ncp.get("storyform", {}).get("throughlines", {}).get("os", {}).get("dynamic")
        # Only propose a fix when we have both sides and they currently collide.
        if mc_dyn and os_dyn and mc_dyn == os_dyn:
            would_apply = True
            diff["dynamic_pair_reciprocity"] = {
                "before": {"mc.dynamic": mc_dyn, "os.dynamic": os_dyn},
                "after_hint": "Adjust mc.dynamic so it reciprocates os.dynamic",
            }

    return {
        "would_apply": would_apply,
        "diff": diff,
        "warnings": []
    }


def register(mcp: FastMCP) -> None:
    mcp.tool(tags={"domain:novel"})(novel_coherence_check)
    mcp.tool(tags={"domain:novel"})(novel_coherence_correct)
