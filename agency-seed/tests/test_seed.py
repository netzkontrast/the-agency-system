"""The seed's proof. Runs on the REAL substrate (graphqlite + fastmcp).

Proves:
  1. THE MOAT — cross-concern provenance is one graph traversal.
  2. The verb frame + one graph carry TWO genuinely different capabilities
     (a stateless `transform` and an `agent`) — the panel's falsifier.
  3. Bi-temporal memory: the *what* changes while the *why* holds (as-of).
  4. COMPLETED != done (the jules silent-fail lesson) as a first-class step.
  5. The four-verb engine over real FastMCP, with MCP-conformant names.
  6. Real code-mode: raw tools hidden behind search/get_schema/execute; an
     execute() block filters in-sandbox and returns only a delta.
"""
import asyncio
import json
import os
import re
import subprocess
import sys
import tempfile

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


def run_scenario(e: Engine) -> str:
    """capture→confirm intent, open an agent lifecycle, run two different
    capabilities, pass a gate, complete. Returns the intent id."""
    iid = e.intent.capture("ship green CI", "auth test passes", "tests green")
    e.intent.confirm(iid)
    lc = e.lifecycle.open(iid, agent="jules")
    # a REAL transform capability
    e.registry.invoke(e.memory, iid, "syllables", "count", text="fix the failing auth test")
    # an agent capability (produces an artefact, BY the agent)
    e.registry.invoke(e.memory, iid, "jules", "patch",
                      agent_id="agent:jules", spec="fix auth", pushed=True)
    assert e.lifecycle.move(lc, "tests-green", ok=True) == "working"
    assert e.lifecycle.complete(lc) == "completed"
    return iid


def test_provenance_moat():
    e = fresh()
    iid = run_scenario(e)
    prov = e.memory.provenance(iid)

    verbs = sorted(n["verb"] for n in prov["serves"] if "verb" in n)
    assert verbs == ["count", "patch"]                      # two different crafts, one graph
    assert {n["role"] for n in prov["serves"] if "role" in n} == {"transform", "act"}
    assert any(a["id"] == "agent:jules" for a in prov["agents"])     # the agent that ran it
    assert any(p["kind"] == "patch" for p in prov["artefacts"])      # what it produced
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
    e = fresh()
    iid = e.intent.capture("x", "y", "z")
    paused, _ = e.registry.invoke(e.memory, iid, "jules", "patch",
                                  agent_id="agent:jules", spec="s", pushed=False)
    assert paused["status"] == "COMPLETED"
    assert e.registry.invoke(e.memory, iid, "jules", "verify",
                             branch_pushed=paused["branch_pushed"])[0]["done"] is False
    assert e.registry.invoke(e.memory, iid, "jules", "verify",
                             branch_pushed=True)[0]["done"] is True
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
    e = fresh()
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
            f"p = val(await call_tool('capability_jules_patch', {{'spec': best_line, 'intent_id': '{iid}', 'agent_id': 'agent:jules', 'pushed': True}}))\n"
            "return {'max_syllables': best_n, 'patched_line': best_line, 'status': p['status']}\n"
        )
        return _sc(await mcp.call_tool("execute", {"code": code}))

    delta = asyncio.run(main())
    # the single small delta returned from many in-sandbox calls (token-efficient)
    assert delta["max_syllables"] == 6
    assert delta["patched_line"] == "fix the failing auth test"
    assert delta["status"] == "COMPLETED"

    # the executable chain is now a connected provenance subgraph
    prov = e.memory.provenance(iid)
    verbs = sorted(n["verb"] for n in prov["serves"] if "verb" in n)
    assert verbs == ["count", "count", "count", "patch"]      # 3 transforms + 1 act, chained
    assert any(a["id"] == "agent:jules" for a in prov["agents"])
    assert any(p["kind"] == "patch" for p in prov["artefacts"])
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
