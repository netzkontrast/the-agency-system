"""The seed's proof. Runs on the REAL substrate (graphqlite + fastmcp).

Proves (10 tests): the provenance moat; one graph carries two different
capabilities (a transform + a REAL agent); bi-temporal memory; COMPLETED != done
(real Jules verify); code-mode IS the contract (search/get_schema/execute);
code-mode tool-chaining; gates via elicit; bash<->MCP isomorphism; schemas &
templates; a strictly-enforced ontology; and a micro-step skill walker with a
hard gate.
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

from agency_seed.engine import Engine

SEED_DIR = os.path.dirname(os.path.dirname(__file__))
# code that chains one tool and returns just the int delta (handles either result shape)
_COUNT_CODE = (
    "r = await call_tool('capability_syllables_count', "
    "{{'text': '{text}', 'intent_id': '{iid}'}})\n"
    "return r['result'] if isinstance(r, dict) and 'result' in r else r"
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


class FakeJulesClient:
    """Boundary stand-in for the external Jules API (deterministic tests). The
    REAL client (RealJulesClient -> jules_create/jules_get) is the default in the
    engine and is proven live (PR #175)."""
    def __init__(self, state: str = "completed"):
        self._state = state

    def create(self, prompt: str, source: str, starting_branch: str) -> dict:
        return {"id": "sessions/123", "state": self._state,
                "url": "https://jules.google.com/session/123"}

    def get(self, session: str) -> dict:
        return {"state": self._state, "url": "https://jules.google.com/session/123"}


def run_scenario(e: Engine) -> str:
    """capture→confirm intent, open an agent lifecycle, run two different
    capabilities, pass a gate, complete. Returns the intent id."""
    iid = e.intent.capture("ship green CI", "auth test passes", "tests green")
    e.intent.confirm(iid)
    lc = e.lifecycle.open(iid, agent="jules")
    # a REAL transform capability
    e.registry.invoke(e.memory, iid, "syllables", "count", text="fix the failing auth test")
    # the agent capability — really dispatches Jules (stand-in client at the boundary)
    e.registry.invoke(e.memory, iid, "jules", "dispatch", agent_id="agent:jules",
                      source="netzkontrast/the-agency-system", starting_branch="main",
                      prompt="fix auth", client=FakeJulesClient())
    assert e.lifecycle.move(lc, "tests-green", ok=True) == "working"
    assert e.lifecycle.complete(lc) == "completed"
    return iid


def test_provenance_moat():
    e = fresh()
    iid = run_scenario(e)
    prov = e.memory.provenance(iid)

    verbs = sorted(n["verb"] for n in prov["serves"] if "verb" in n)
    assert verbs == ["count", "dispatch"]                   # two different crafts, one graph
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
                                client=FakeJulesClient(state="completed"))
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
        hits = str(_sc(await mcp.call_tool("search", {"query": "syllables count"})))
        assert "capability_syllables_count" in hits          # discovery via search
        out = _sc(await mcp.call_tool("execute", {
            "code": _COUNT_CODE.format(text="hello brave world", iid=iid)}))
        return int(out)

    assert asyncio.run(main()) == 4                           # called from inside execute
    assert any(x["verb"] == "count" for x in e.memory.provenance(iid)["serves"])
    e.memory.close()


def test_codemode_chaining_is_an_executable_graph():
    """Code-mode chains different tools in plain Python — the code IS an
    executable dataflow graph. Token efficiency: 4 tool calls run in-sandbox,
    only ONE small delta crosses into context. And because every call_tool
    records an Invocation, that executable graph is MIRRORED into the durable
    provenance graph (transform → agent, both edged to the intent)."""
    e = Engine(tempfile.mktemp(suffix=".db"), jules_client=FakeJulesClient())  # boundary stand-in
    iid = e.intent.capture("ship green CI", "auth test passes", "tests green")
    e.intent.confirm(iid)
    e.lifecycle.open(iid, agent="jules")                      # so agent:jules exists
    mcp = e.build_mcp(codemode=True)

    async def main():
        names = {t.name for t in await mcp.list_tools()}
        assert names == {"search", "get_schema", "execute"}   # raw tools hidden
        code = (
            "def val(x):\n"
            "    return x['result'] if isinstance(x, dict) and 'result' in x else x\n"
            "lines = ['fix the failing auth test', 'add retry', 'ship']\n"
            "scored = []\n"
            "for ln in lines:\n"
            f"    r = await call_tool('capability_syllables_count', {{'text': ln, 'intent_id': '{iid}'}})\n"
            "    scored.append((int(val(r)), ln))\n"
            "scored.sort(reverse=True)\n"
            "best_n, best_line = scored[0]\n"
            "# chain: the transform's output feeds the agent capability\n"
            f"p = val(await call_tool('capability_jules_dispatch', {{'source': 'o/r', 'starting_branch': 'main', 'prompt': best_line, 'intent_id': '{iid}', 'agent_id': 'agent:jules'}}))\n"
            "return {'max_syllables': best_n, 'patched_line': best_line, 'status': p['status']}\n"
        )
        return _sc(await mcp.call_tool("execute", {"code": code}))

    delta = asyncio.run(main())
    # the single small delta returned from many in-sandbox calls (token-efficient)
    assert delta["max_syllables"] == 6
    assert delta["patched_line"] == "fix the failing auth test"
    assert delta["status"] == "completed"

    # the executable chain is now a connected provenance subgraph
    prov = e.memory.provenance(iid)
    verbs = sorted(n["verb"] for n in prov["serves"] if "verb" in n)
    assert verbs == ["count", "count", "count", "dispatch"]   # 3 transforms + 1 effect, chained
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
    iid = e.intent.capture("make a track sheet", "sheet for T1", "valid sheet")
    e.intent.confirm(iid)
    schema = e.memory.record("Schema", {"name": "track-sheet", "required": "title,lyrics"})
    template = e.memory.record("Template", {"name": "track-sheet", "body": "# {title}\n\n{lyrics}"})

    # generate the artefact from the template
    data = {"title": "Test Track", "lyrics": "la la la"}
    body = e.memory.recall(template)["body"].format(**data)
    art = e.memory.record("Artefact", {"kind": "track-sheet", **data, "body": body})
    e.memory.link(art, template, "DERIVED_FROM")
    e.memory.link(art, iid, "SERVES")

    # validate against the schema (the typed layer)
    assert e.memory.validate_schema(art, schema) is True
    e.memory.link(art, schema, "VALIDATES_AGAINST")
    assert "# Test Track" in body and "la la la" in body

    # the schema bites: an artefact missing a required field fails
    bad = e.memory.record("Artefact", {"kind": "track-sheet", "title": "x"})
    assert e.memory.validate_schema(bad, schema) is False

    # the typed/generative edges live in the one graph
    rows = e.memory.g.query(
        "MATCH (a:Artefact)-[:VALIDATES_AGAINST]->(s:Schema) RETURN s")
    assert any(r["s"]["properties"].get("name") == "track-sheet" for r in rows)
    drv = e.memory.g.query("MATCH (a:Artefact)-[:DERIVED_FROM]->(t:Template) RETURN t")
    assert any(r["t"]["properties"].get("name") == "track-sheet" for r in drv)
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
    code = _COUNT_CODE.format(text="fix the failing auth test", iid=iid)

    # (1) MCP path — code-mode contract in-process
    mcp_out = _sc(asyncio.run(e.build_mcp(codemode=True).call_tool("execute", {"code": code})))
    e.memory.close()                                          # release the lock for the subprocess

    # (2) bash path — the same contract via a shell-only invocation
    proc = subprocess.run(
        [sys.executable, "-m", "agency_seed.cli", "--db", db, "execute", "--code", code],
        cwd=SEED_DIR, capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": SEED_DIR},
    )
    assert proc.returncode == 0, proc.stderr
    cli_out = json.loads(proc.stdout)

    assert int(mcp_out) == int(cli_out) == 6                  # identical across harnesses
    # shared durable graph: both runs recorded into the one graph
    e2 = Engine(db)
    counts = [n for n in e2.memory.provenance(iid)["serves"] if n.get("verb") == "count"]
    assert len(counts) == 2                                   # one via MCP, one via bash CLI
    e2.memory.close()


def test_ontology_is_strictly_enforced():
    """The strict schemata are enforced on the real graph: an out-of-schema node
    and an unknown edge both raise — the ontology cannot silently drift. And the
    real bitwize conceptualizer ports as a strict 7-phase skill with a hard final
    gate (the micro-step-skill template)."""
    from agency_seed import ontology
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
    from agency_seed import ontology
    from agency_seed.skill import SkillRun
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
