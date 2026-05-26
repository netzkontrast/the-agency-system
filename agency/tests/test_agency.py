"""The seed's proof. Runs on the REAL substrate (graphqlite + fastmcp).

Proves: the provenance moat; one graph carries two genuinely different
capabilities (the plugin-dev craft + the REAL Jules agent); bi-temporal memory;
COMPLETED != done (real Jules verify); code-mode IS the contract
(search/get_schema/execute); code-mode tool-chaining; gates via elicit;
bash<->MCP isomorphism; schemas & templates; a strictly-enforced ontology; a
micro-step skill walker with a hard gate; and the plugin-development capability —
a complete port of the superpowers skill-creation + plugin-authoring skills,
plus a self-hosted Claude Code install that maps macroskills -> micro-skills.
"""
import asyncio
import json
import os
import re
import subprocess
import sys
import tempfile

import pytest
from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult

from agency import install, ontology
from agency.capabilities.plugin import lint_skill
from agency.engine import Engine
from agency.skill import SkillRun

SEED_DIR = os.path.dirname(os.path.dirname(__file__))
# code that lints a (deliberately bad) skill and returns just the violation count
_LINT_CODE = (
    "r = await call_tool('capability_plugin_lint_skill', "
    "{{'name': '{name}', 'description': '{desc}', 'intent_id': '{iid}'}})\n"
    "v = r['result'] if isinstance(r, dict) and 'result' in r else r\n"
    "return len(v['violations'])\n"
)

NAME_RE = re.compile(r"^[a-zA-Z0-9_]{1,64}$")  # MCP / Claude-frontend strict


def fresh() -> Engine:
    return Engine(tempfile.mktemp(suffix=".db"))


def _sc(result):
    sc = result.structured_content
    if isinstance(sc, dict):
        return sc.get("result", sc)
    if sc is not None:
        return sc
    # scalar returns (e.g. execute returning an int) arrive as text content
    if result.content:
        txt = result.content[0].text
        try:
            return json.loads(txt)
        except (ValueError, TypeError):
            return txt
    return None


class StubJulesClient:
    """Boundary stand-in for the external Jules API (deterministic tests). The
    default backend (`JulesClient` -> the vendored `_jules_api`) is what the
    engine uses in production."""
    def __init__(self, state: str = "completed"):
        self._state = state

    def create(self, prompt: str, source: str, starting_branch: str) -> dict:
        return {"id": "sessions/123", "state": self._state,
                "url": "https://jules.google.com/session/123"}

    def get(self, session: str) -> dict:
        return {"state": self._state, "url": "https://jules.google.com/session/123"}


def run_scenario(e: Engine) -> str:
    """capture→confirm intent, open an agent lifecycle, run two genuinely
    different capabilities (a plugin-dev transform + the agent), pass a gate,
    complete. Returns the intent id."""
    iid = e.intent.capture("ship green CI", "auth test passes", "tests green")
    e.intent.confirm(iid)
    lc = e.lifecycle.open(iid, agent="jules")
    # a craft capability — validate a candidate skill (the writing-skills CSO linter)
    e.registry.invoke(e.memory, iid, "plugin", "lint_skill",
                      name="fix-auth", description="Use when the auth test fails")
    # the agent capability — really dispatches Jules (stand-in client at the boundary)
    e.registry.invoke(e.memory, iid, "jules", "dispatch", agent_id="agent:jules",
                      source="netzkontrast/the-agency-system", starting_branch="main",
                      prompt="fix auth", client=StubJulesClient())
    assert e.lifecycle.move(lc, "tests-green", ok=True) == "working"
    assert e.lifecycle.complete(lc) == "completed"
    return iid


def test_provenance_moat():
    e = fresh()
    iid = run_scenario(e)
    prov = e.memory.provenance(iid)

    verbs = sorted(n["verb"] for n in prov["serves"] if "verb" in n)
    assert verbs == ["dispatch", "lint_skill"]              # two different crafts, one graph
    assert {n["role"] for n in prov["serves"] if "role" in n} == {"transform", "effect"}
    assert any(a["id"] == "agent:jules" for a in prov["agents"])     # the agent that ran it
    assert any(p["kind"] == "jules-session" for p in prov["artefacts"])  # what it produced
    assert any(g["name"] == "tests-green" for g in prov["gates"])    # the gate it passed
    e.memory.close()


def test_bitemporal_what_changes_why_holds():
    e = fresh()
    iid = e.intent.capture("ship green CI", "fix auth test", "tests green")
    before = e.memory._tick
    new_id = e.intent.amend(iid, deliverable="fix auth AND token refresh")
    # old version still reconstructable as-of `before`; purpose (why) unchanged
    old = e.memory.recall(iid, as_of=before)
    assert old["deliverable"] == "fix auth test"
    assert e.memory.recall(new_id)["deliverable"] == "fix auth AND token refresh"
    assert e.memory.recall(new_id)["purpose"] == "ship green CI"
    e.memory.close()


def test_completed_not_done():
    """COMPLETED != done: a Jules session reports state=completed even when it
    paused before pushing. `verify` returns done only when a branch is actually
    on remote — the real silent-fail guard (CLAUDE.md JULES_PROTOCOL §8)."""
    e = fresh()
    iid = e.intent.capture("x", "y", "z")
    disp, _ = e.registry.invoke(e.memory, iid, "jules", "dispatch", agent_id="agent:j",
                                source="o/r", starting_branch="main", prompt="do x",
                                client=StubJulesClient(state="completed"))
    assert disp["status"] == "completed"
    # state says completed, but no branch on remote -> NOT done (the silent-fail)
    assert e.registry.invoke(e.memory, iid, "jules", "verify",
                             state=disp["status"], branch_on_remote=False)[0]["done"] is False
    # branch actually on origin -> done
    assert e.registry.invoke(e.memory, iid, "jules", "verify",
                             state=disp["status"], branch_on_remote=True)[0]["done"] is True
    e.memory.close()


def test_codemode_is_the_contract():
    """No four-verb surface. The engine exposes exactly search/get_schema/execute;
    tools are discovered via search and called from inside execute. Lean."""
    e = fresh()
    iid = e.intent.capture("a", "b", "c")
    mcp = e.build_mcp()                                       # default: code-mode IS the contract

    async def main():
        names = {t.name for t in await mcp.list_tools()}
        assert names == {"search", "get_schema", "execute"}  # the whole contract
        assert all(NAME_RE.match(n) for n in names)
        hits = str(_sc(await mcp.call_tool("search", {"query": "lint skill"})))
        assert "capability_plugin_lint_skill" in hits        # discovery via search
        out = _sc(await mcp.call_tool("execute", {
            "code": _LINT_CODE.format(name="Bad Name", desc="does stuff", iid=iid)}))
        return int(out)

    assert asyncio.run(main()) == 2                           # bad name + missing "Use when"
    assert any(x["verb"] == "lint_skill" for x in e.memory.provenance(iid)["serves"])
    e.memory.close()


def test_codemode_chaining_is_an_executable_graph():
    """Code-mode chains different tools in plain Python — the code IS an
    executable dataflow graph. Token efficiency: many tool calls run in-sandbox,
    only ONE small delta crosses into context. And because every call_tool records
    an Invocation, that executable graph is MIRRORED into the durable provenance
    graph (the transform's pick feeds the agent, both edged to the intent)."""
    e = Engine(tempfile.mktemp(suffix=".db"), jules_client=StubJulesClient())  # boundary stand-in
    iid = e.intent.capture("ship a clean skill", "skill authored + dispatched", "lint clean")
    e.intent.confirm(iid)
    e.lifecycle.open(iid, agent="jules")                      # so agent:jules exists
    mcp = e.build_mcp(codemode=True)

    async def main():
        names = {t.name for t in await mcp.list_tools()}
        assert names == {"search", "get_schema", "execute"}   # raw tools hidden
        code = (
            "def val(x):\n"
            "    return x['result'] if isinstance(x, dict) and 'result' in x else x\n"
            "cands = [('alpha skill', 'does things'), ('good-skill', 'Use when you ship code'), ('ok-skill', 'manage things')]\n"
            "scored = []\n"
            "for nm, desc in cands:\n"
            f"    r = val(await call_tool('capability_plugin_lint_skill', {{'name': nm, 'description': desc, 'intent_id': '{iid}'}}))\n"
            "    scored.append((len(r['violations']), nm))\n"
            "scored.sort()\n"
            "best_v, best_name = scored[0]\n"
            "# chain: the linter's pick feeds the agent capability\n"
            f"p = val(await call_tool('capability_jules_dispatch', {{'source': 'o/r', 'starting_branch': 'main', 'prompt': best_name, 'intent_id': '{iid}', 'agent_id': 'agent:jules'}}))\n"
            "return {'min_violations': best_v, 'chosen': best_name, 'status': p['status']}\n"
        )
        return _sc(await mcp.call_tool("execute", {"code": code}))

    delta = asyncio.run(main())
    # the single small delta returned from many in-sandbox calls (token-efficient)
    assert delta["min_violations"] == 0
    assert delta["chosen"] == "good-skill"
    assert delta["status"] == "completed"

    # the executable chain is now a connected provenance subgraph
    prov = e.memory.provenance(iid)
    verbs = sorted(n["verb"] for n in prov["serves"] if "verb" in n)
    assert verbs == ["dispatch", "lint_skill", "lint_skill", "lint_skill"]  # 3 transforms + 1 effect, chained
    assert any(a["id"] == "agent:jules" for a in prov["agents"])
    assert any(p["kind"] == "jules-session" for p in prov["artefacts"])
    e.memory.close()


def test_gate_elicits_human_in_flow():
    """A gate/intent-verification step ELICITS a decision mid-flow (askuser in the
    flow): a one-line prompt streams to the human/agent, the answer resumes the
    chain, and the outcome is recorded as a Gate in the provenance graph. This is
    the atomic, token-tiny human-in-the-loop step."""
    e = fresh()
    iid = e.intent.capture("ship the release", "v1 published", "human approves")
    e.intent.confirm(iid)
    lc = e.lifecycle.open(iid, agent="jules")
    mcp = e.build_mcp(codemode=False)

    async def approve(message, response_type, params, context):
        return ElicitResult(action="accept", content="approve")   # simulate the human

    async def main():
        async with Client(mcp, elicitation_handler=approve) as client:
            r = await client.call_tool("lifecycle_gate", {
                "question": "Approve release?", "intent_id": iid, "lifecycle_id": lc,
            })
            return _sc(r)

    out = asyncio.run(main())
    assert out["approved"] is True
    # the human-in-the-loop verification is now a gate in the provenance graph
    prov = e.memory.provenance(iid)
    assert any(g["name"] == "human-confirm" and g["passed"] for g in prov["gates"])
    e.memory.close()


def test_schemas_and_templates_typed_generative():
    """The typed/generative layer. A Template GENERATES an Artefact (the `act`),
    a Schema VALIDATES it (the typed contract) — both are ordinary nodes in the
    one graph; the artefact is DERIVED_FROM the template and VALIDATES_AGAINST the
    schema. The schema also bites: a missing field fails validation."""
    e = fresh()
    iid = e.intent.capture("make a doc", "doc for X", "valid doc")
    e.intent.confirm(iid)
    schema = e.memory.record("Schema", {"name": "doc-sheet", "required": "title,body"})
    template = e.memory.record("Template", {"name": "doc-sheet", "body": "# {title}\n\n{body}"})

    # generate the artefact from the template
    data = {"title": "Test Doc", "body": "the content"}
    body = e.memory.recall(template)["body"].format(**data)
    art = e.memory.record("Artefact", {"kind": "doc-sheet", **data})
    e.memory.link(art, template, "DERIVED_FROM")
    e.memory.link(art, iid, "SERVES")

    # validate against the schema (the typed layer)
    assert e.memory.validate_schema(art, schema) is True
    e.memory.link(art, schema, "VALIDATES_AGAINST")
    assert "# Test Doc" in body and "the content" in body

    # the schema bites: an artefact missing a required field fails
    bad = e.memory.record("Artefact", {"kind": "doc-sheet", "title": "x"})
    assert e.memory.validate_schema(bad, schema) is False

    # the typed/generative edges live in the one graph
    rows = e.memory.g.query(
        "MATCH (a:Artefact)-[:VALIDATES_AGAINST]->(s:Schema) RETURN s")
    assert any(r["s"]["properties"].get("name") == "doc-sheet" for r in rows)
    drv = e.memory.g.query("MATCH (a:Artefact)-[:DERIVED_FROM]->(t:Template) RETURN t")
    assert any(r["t"]["properties"].get("name") == "doc-sheet" for r in drv)
    e.memory.close()


def test_isomorphism_mcp_equals_bash_cli():
    """Harness-in-harness: the SAME code-mode contract, driven via MCP in-process
    AND via a bash-only subprocess (no MCP client, no Skill loader — what Jules
    has), over the SAME persisted graph, yields identical results — and both
    invocations land in one graph. MCP ≡ bash, proven."""
    db = tempfile.mktemp(suffix=".db")
    e = Engine(db)
    iid = e.intent.capture("ship green CI", "auth test passes", "tests green")
    e.intent.confirm(iid)
    code = _LINT_CODE.format(name="Bad Name", desc="does stuff", iid=iid)

    # (1) MCP path — code-mode contract in-process
    mcp_out = _sc(asyncio.run(e.build_mcp(codemode=True).call_tool("execute", {"code": code})))
    e.memory.close()                                          # release the lock for the subprocess

    # (2) bash path — the same contract via a shell-only invocation
    proc = subprocess.run(
        [sys.executable, "-m", "agency.cli", "--db", db, "execute", "--code", code],
        cwd=SEED_DIR, capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": SEED_DIR},
    )
    assert proc.returncode == 0, proc.stderr
    cli_out = json.loads(proc.stdout)

    assert int(mcp_out) == int(cli_out) == 2                  # identical across harnesses
    # shared durable graph: both runs recorded into the one graph
    e2 = Engine(db)
    lints = [n for n in e2.memory.provenance(iid)["serves"] if n.get("verb") == "lint_skill"]
    assert len(lints) == 2                                    # one via MCP, one via bash CLI
    e2.memory.close()


def test_ontology_is_strictly_enforced():
    """The strict schemata are enforced on the real graph: an out-of-schema node
    and an unknown edge both raise — the ontology cannot silently drift. And the
    real bitwize conceptualizer ports as a strict 7-phase skill with a hard final
    gate (the micro-step-skill template)."""
    e = fresh()
    with pytest.raises(ValueError):                          # missing required Intent fields
        e.memory.record("Intent", {"purpose": "x"})
    iid = e.intent.capture("a", "b", "c")
    agent = e.memory.record("Agent", {"runtime": "local"}, node_id="agent:x")
    with pytest.raises(ValueError):                          # unknown edge type
        e.memory.link(agent, iid, "FROBNICATES")
    sk = ontology.ALBUM_CONCEPT_SKILL                        # the conceptualizer, schematized
    assert len(sk["phases"]) == 7
    assert sk["phases"][-1].get("gate") == "hard"            # Phase 7 = hard gate
    assert all(p["produces"] for p in sk["phases"])          # every phase declares its required outputs
    e.memory.close()


def test_skill_walker_micro_steps_with_hard_gate():
    """A skill walks ONE phase at a time (progressive disclosure), validates each
    phase's required outputs before advancing, and the hard-gate final phase
    blocks until explicitly confirmed. The run records itself as provenance."""
    e = fresh()
    iid = e.intent.capture("plan an album", "album concept", "user confirms")
    run = SkillRun(e.memory, iid, ontology.ALBUM_CONCEPT_SKILL)

    assert run.current()["index"] == 1 and "artist" in run.current()["produces"]
    with pytest.raises(ValueError):                          # missing required outputs
        run.submit({"artist": "x"})

    fills = {
        "foundation": {"artist": "a", "genre": "g", "type": "thematic",
                       "scale": "ep", "theme": "t", "true_story": "no"},
        "concept": {"key_subjects": "k", "emotional_core": "e", "why": "w"},
        "sonic": {"references": "r", "production_style": "p", "vocal_approach": "v",
                  "instrumentation": "i", "mood": "m", "target_duration": "4:00"},
        "structure": {"tracklist": "t", "sequencing": "s", "energy_map": "e"},
        "art": {"visual_concept": "v", "palette": "p", "symbols": "s"},
        "practical": {"album_title": "t", "track_titles": "t", "research_needs": "n",
                      "explicit": "no", "distributor_genres": "g"},
    }
    for name, out in fills.items():
        assert run.current()["name"] == name                 # disclosed one at a time
        assert run.submit(out)["status"] == "working"

    assert run.current()["gate"] == "hard"                   # Phase 7 = hard gate
    assert run.submit({"user_confirmed": "yes"}, confirmed=False)["status"] == "input-required"
    assert run.submit({"user_confirmed": "yes"}, confirmed=True)["status"] == "completed"
    assert run.done

    rows = e.memory.g.query("MATCH (s:Skill)-[:HAS_PHASE]->(p:Phase) RETURN p")
    assert len(rows) == 7                                     # the whole run is provenance
    e.memory.close()


def test_real_skill_executes_tools():
    """The COMPLETE port of writing-skills as an executable micro-step skill: the
    Iron Law ("no skill without a failing test first") is enforced by ordering —
    the walker cannot reach GREEN (author_skill) until RED produced its baseline.
    The GREEN + lint phases run REAL capability verbs (recorded as Invocations)."""
    e = fresh()
    iid = e.intent.capture("write a skill", "deployed skill", "human approves")
    run = SkillRun(e.memory, iid, e.ontology.skill("skill-creation"), registry=e.registry)

    # RED: baseline first (the Iron Law, enforced by phase ordering)
    assert run.current()["name"] == "red-baseline"
    assert run.submit({"baseline": "agent skips the failing test",
                       "rationalizations": "'too simple to test'"})["status"] == "working"
    # GREEN: author the skill (a REAL act verb runs)
    assert run.current()["name"] == "green-author"
    assert run.submit({"name": "my-skill", "description": "Use when you need X",
                       "body": "# My Skill\nbody"})["status"] == "working"
    assert any(n.get("verb") == "author_skill" for n in e.memory.provenance(iid)["serves"])
    # lint against the CSO rules (a REAL transform verb runs)
    assert run.current()["name"] == "lint"
    assert run.submit({"name": "my-skill", "description": "Use when you need X"})["status"] == "working"
    assert any(n.get("verb") == "lint_skill" for n in e.memory.provenance(iid)["serves"])
    # REFACTOR
    assert run.submit({"rationalization_table": "| excuse | reality |",
                       "red_flags": "code before test"})["status"] == "working"
    # deploy hard gate (STOP before next skill)
    assert run.current()["gate"] == "hard"
    assert run.submit({"user_confirmed": "yes"}, confirmed=False)["status"] == "input-required"
    assert run.submit({"user_confirmed": "yes"}, confirmed=True)["status"] == "completed"
    assert run.done
    e.memory.close()


def test_strict_enums_enforced_on_both_write_paths():
    """Design-loop refinement: closed enums are ENFORCED, not decorative. A bad
    role or lifecycle state raises — on record AND on the update mutation path."""
    e = fresh()
    iid = e.intent.capture("a", "b", "c")
    with pytest.raises(ValueError):                          # role not in ROLES
        e.memory.record("Invocation", {"capability": "x", "verb": "y", "role": "banana"})
    with pytest.raises(ValueError):                          # state not in LIFECYCLE_STATES
        e.memory.record("Lifecycle", {"state": "bogus", "phase": 0})
    lc = e.lifecycle.open(iid)                                # valid state via record
    with pytest.raises(ValueError):                          # update path is guarded too
        e.memory.update(lc, {"state": "bogus"})
    e.memory.close()


def test_plugin_capability_generates_valid_artefacts():
    """The plugin-development capability (ported from superpowers writing-skills +
    plugin authoring): every `act` verb renders a REAL artefact from a strict
    template, recorded as provenance and validating against its strict Schema."""
    e = fresh()
    iid = e.intent.capture("author a plugin", "plugin files", "valid")
    e.intent.confirm(iid)
    reg, mem = e.registry, e.memory

    res, _ = reg.invoke(mem, iid, "plugin", "scaffold",
                        name="demo", version="0.1.0", description="A demo plugin")
    manifest = json.loads(res["result"])                     # a real, valid JSON manifest
    assert manifest["name"] == "demo" and manifest["version"] == "0.1.0"

    # the artefact is provenance and validates against a strict Schema
    art_id = next(a["id"] for a in mem.provenance(iid)["artefacts"] if a["kind"] == "plugin-manifest")
    schema = mem.record("Schema", {"name": "plugin-manifest",                # schema OWNED by the capability
                                   "required": ",".join(e.ontology.schemas["plugin-manifest"])})
    assert mem.validate_schema(art_id, schema) is True
    # the schema bites: a manifest missing `version` fails
    bad = mem.record("Artefact", {"kind": "plugin-manifest", "name": "x"})
    assert mem.validate_schema(bad, schema) is False

    sk, _ = reg.invoke(mem, iid, "plugin", "author_skill",
                       name="my-skill", description="Use when you need X", body="# My Skill\nbody")
    assert sk["result"].startswith("---\nname: my-skill")    # the skill creator emits frontmatter
    reg.invoke(mem, iid, "plugin", "author_command", name="go", description="Use when go", body="do it")
    me, _ = reg.invoke(mem, iid, "plugin", "marketplace_entry",
                       name="demo", version="0.1.0", description="d", source="netzkontrast/agency")
    src = json.loads(me["result"])["source"]                 # owner/name -> github object (spec)
    assert src == {"source": "github", "repo": "netzkontrast/agency"}
    reg.invoke(mem, iid, "plugin", "step_doc", step="manifest", output="written")

    kinds = {a["kind"] for a in mem.provenance(iid)["artefacts"]}
    assert {"plugin-manifest", "skill-md", "command-md", "marketplace-entry", "step-doc"} <= kinds
    e.memory.close()


def test_lint_skill_ports_cso_rules():
    """The writing-skills CSO rules ported as ENFORCEABLE compute (judgment as
    code): a clean skill passes; bad name, missing 'Use when…', first person, and
    over-length descriptions are each flagged."""
    assert lint_skill("good-name", "Use when you ship code")["ok"] is True
    bad = lint_skill("Bad Name", "does stuff")
    assert bad["ok"] is False
    assert any("letters, numbers, hyphens" in v for v in bad["violations"])
    assert any("Use when" in v for v in bad["violations"])
    assert any("third person" in v for v in lint_skill("ok-name", "Use when I help you")["violations"])
    assert any("500" in v for v in lint_skill("ok-name", "Use when " + "x" * 600)["violations"])


def test_plugin_dev_skill_each_step_yields_a_document():
    """The plugin-dev chain walks one phase at a time and EACH step yields a
    prestructured document (the bitwize 'resulting document of each step' pattern,
    made strict + provenance-recorded): manifest → skill → command → marketplace
    entry → hard confirm gate."""
    e = fresh()
    iid = e.intent.capture("develop a plugin", "a Claude Code plugin", "user confirms")
    run = SkillRun(e.memory, iid, e.ontology.skill("plugin-dev"), registry=e.registry)

    assert run.current()["name"] == "manifest"
    assert run.submit({"name": "demo", "version": "0.1.0", "description": "A demo"})["status"] == "working"
    assert run.submit({"name": "demo-skill", "description": "Use when you demo", "body": "# Demo"})["status"] == "working"
    assert run.submit({"name": "go", "description": "Use when go", "body": "do it"})["status"] == "working"
    assert run.submit({"name": "demo", "version": "0.1.0", "description": "A demo",
                       "source": "netzkontrast/agency"})["status"] == "working"
    assert run.current()["gate"] == "hard"
    assert run.submit({"user_confirmed": "yes"}, confirmed=False)["status"] == "input-required"
    assert run.submit({"user_confirmed": "yes"}, confirmed=True)["status"] == "completed"

    kinds = {a["kind"] for a in e.memory.provenance(iid)["artefacts"]}
    assert {"plugin-manifest", "skill-md", "command-md", "marketplace-entry"} <= kinds
    e.memory.close()


def test_help_maps_macroskills_to_microskills():
    """The `help` discovery surface maps the engine's capabilities (macroskills)
    to their verbs (the harness-in-harness micro-skills) over the LIVE registry —
    and syllables is gone (it belongs to a future Music capability)."""
    e = fresh()
    iid = e.intent.capture("discover", "the capability map", "ok")
    mcp = e.build_mcp(codemode=False)

    async def main():
        return _sc(await mcp.call_tool("capability_plugin_help", {"intent_id": iid}))

    out = asyncio.run(main())
    m = out["map"]
    assert {"plugin", "jules", "reflect"} <= set(m)
    assert "syllables" not in m
    assert {"scaffold", "author_skill", "lint_skill", "help"} <= set(m["plugin"])
    assert {"dispatch", "verify"} <= set(m["jules"])
    e.memory.close()


def test_agency_plugin_install_is_self_hosted():
    """The Agency Plugin for Claude Code install is SELF-HOSTED: the committed
    manifest, `help` macroskill, and command are exactly what the plugin-dev
    capability regenerates from the live registry — and the help skill passes its
    own CSO linter (the engine authors, and validates, its own plugin)."""
    e = fresh()
    files = install.generate(e)
    e.memory.close()
    for rel, content in files.items():                       # committed == regenerated (dogfood)
        with open(os.path.join(SEED_DIR, rel)) as f:
            assert f.read() == content, rel
    manifest = json.loads(files[".claude-plugin/plugin.json"])
    assert {"name", "version", "description"} <= set(manifest)
    assert lint_skill("help", install.HELP_DESC)["ok"] is True


def test_ontology_extends_strictly_from_capabilities():
    """The ontology is EXTENSIBLE: the core defines a base, and each capability
    contributes its own node types/skills/schemas, merged strictly onto the core.
    A bare core lacks `Plugin`; the engine's effective ontology has it (from the
    plugin capability) and enforces it in Memory; redefining a core node raises."""
    core = ontology.Ontology.core()
    assert "Intent" in core.nodes and "Plugin" not in core.nodes      # Plugin is NOT core
    assert "skill-creation" not in core.skills                        # nor is the skill-creation skill

    e = fresh()
    assert "Plugin" in e.ontology.nodes                               # contributed by the plugin capability
    assert {"skill-creation", "plugin-dev", "album-concept"} <= set(e.ontology.skills)
    # the extension is LIVE in Memory: the contributed node type is enforced
    with pytest.raises(ValueError):
        e.memory.record("Plugin", {"name": "x"})                      # missing version + description
    assert e.memory.record("Plugin", {"name": "x", "version": "0.1.0", "description": "d"})

    # strict: an extension may not redefine a core node with different fields
    with pytest.raises(ValueError):
        core.extend(ontology.OntologyExtension(nodes={"Intent": ["only_purpose"]}), owner="bad")
    e.memory.close()


def test_reflect_capability_writes_and_recalls():
    """The `reflect` capability — the panel's net-new Memory spec, ported from the
    private-journal plugin and added by DROPPING A FILE in capabilities/. It owns
    its ontology (a Reflection node + scope enum), the engine injects `memory`, and
    its writes are provenance (OBSERVED_DURING the intent)."""
    e = fresh()
    iid = e.intent.capture("learn from the run", "durable notes", "ok")
    e.intent.confirm(iid)
    reg, mem = e.registry, e.memory
    reg.invoke(mem, iid, "reflect", "note", scope="technical",
               text="graphqlite autocommits across connections")
    reg.invoke(mem, iid, "reflect", "note", scope="user", text="prefers terse updates")

    alln = reg.invoke(mem, iid, "reflect", "recall")[0]["result"]
    assert {n["scope"] for n in alln} == {"technical", "user"}            # newest-first list
    tech = reg.invoke(mem, iid, "reflect", "recall", scope="technical")[0]["result"]
    assert len(tech) == 1 and "graphqlite" in tech[0]["text"]
    hits = reg.invoke(mem, iid, "reflect", "search", query="terse")[0]["result"]
    assert len(hits) == 1 and hits[0]["scope"] == "user"

    with pytest.raises(ValueError):                                       # scope enum (owned) bites
        reg.invoke(mem, iid, "reflect", "note", scope="bogus", text="x")
    rows = mem.g.query("MATCH (r:Reflection)-[:OBSERVED_DURING]->(i:Intent) "
                       "WHERE i.id = $iid RETURN r", {"iid": iid})
    assert len(rows) == 2                                                 # reflections are provenance
    e.memory.close()
