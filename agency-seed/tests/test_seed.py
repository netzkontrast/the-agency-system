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
import re
import tempfile

from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult

from agency_seed.engine import Engine

NAME_RE = re.compile(r"^[a-zA-Z0-9_]{1,64}$")  # MCP / Claude-frontend strict


def fresh() -> Engine:
    return Engine(tempfile.mktemp(suffix=".db"))


def _sc(result):
    sc = result.structured_content
    return sc.get("result", sc) if isinstance(sc, dict) else sc


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


def test_four_verb_engine_real_fastmcp():
    e = fresh()
    iid = e.intent.capture("a", "b", "c")
    mcp = e.build_mcp(codemode=False)

    async def main():
        tools = await mcp.list_tools()
        names = {t.name for t in tools}
        assert {"capability_syllables_count", "memory_graph_provenance",
                "agency_list_skills", "agency_dispatch_skill"} <= names
        assert all(NAME_RE.match(n) for n in names)          # MCP-conformant names
        skills = _sc(await mcp.call_tool("agency_list_skills", {}))
        assert "jules" in skills and "syllables" in skills
        n = _sc(await mcp.call_tool("capability_syllables_count",
                                    {"text": "hello brave world", "intent_id": iid}))
        return int(n)

    count = asyncio.run(main())
    assert count == 4                                        # hel-lo brave wor-ld
    # the tool call recorded an Invocation that SERVES the intent
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
