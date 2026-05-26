"""Engine — one FastMCP server + one graph.

**Code-mode IS the contract** (lean: no separate four-verb surface). The engine
exposes exactly `search` / `get_schema` / `execute`; the underlying tools
(capabilities, gate, provenance) are discovered via `search` and called from
inside `execute` (`await call_tool(name, params)`). This is the same surface a
bash agent drives via `agency_seed/cli.py` — so MCP and bash are isomorphic by
construction. Tool names are MCP-conformant `<concept>_<capability>_<verb>`.
"""
from __future__ import annotations

from fastmcp import Context, FastMCP

try:
    from fastmcp.experimental.transforms.code_mode import CodeMode
    HAVE_CODEMODE = True
except ImportError:  # pragma: no cover
    HAVE_CODEMODE = False

from .capability import Registry
from .capabilities import jules_capability, syllables_capability
from .capabilities.jules import RealJulesClient
from .intent import Intent
from .lifecycle import Lifecycle
from .memory import Memory


class Engine:
    def __init__(self, path: str, jules_client=None):
        self.memory = Memory(path)
        self.intent = Intent(self.memory)
        self.lifecycle = Lifecycle(self.memory)
        self.jules_client = jules_client or RealJulesClient()   # boundary: real orchestrator by default
        self.registry = Registry()
        self.registry.register(syllables_capability)
        self.registry.register(jules_capability)

    def build_mcp(self, codemode: bool = True) -> FastMCP:
        transforms = [CodeMode()] if (codemode and HAVE_CODEMODE) else []
        mcp = FastMCP("agency-seed", transforms=transforms)
        reg, mem = self.registry, self.memory

        @mcp.tool
        def capability_syllables_count(text: str, intent_id: str) -> int:
            "Count syllables (transform); recorded as an Invocation that SERVES the intent."
            result, _ = reg.invoke(mem, intent_id, "syllables", "count", text=text)
            return result

        jc = self.jules_client

        @mcp.tool
        def capability_jules_dispatch(source: str, starting_branch: str, prompt: str,
                                      intent_id: str, agent_id: str) -> dict:
            "Dispatch a REAL Jules remote session (effect); records a jules-session artefact BY the agent."
            result, _ = reg.invoke(mem, intent_id, "jules", "dispatch", agent_id=agent_id,
                                   source=source, starting_branch=starting_branch,
                                   prompt=prompt, client=jc)
            return result

        @mcp.tool
        async def lifecycle_gate(question: str, intent_id: str, lifecycle_id: str, ctx: Context) -> dict:
            "An intent-verification gate that ELICITS a human/agent decision mid-flow "
            "(askuser-in-the-flow): a tiny prompt streams out, the answer resumes the chain. "
            "Records the outcome to the provenance graph."
            res = await ctx.elicit(question, response_type=["approve", "reject"])
            approved = getattr(res, "data", None) == "approve"
            g = mem.record("Gate", {"name": "human-confirm", "question": question, "passed": approved})
            mem.link(lifecycle_id, g, "PASSED" if approved else "BLOCKED_ON")
            return {"approved": approved, "gate_id": g}

        @mcp.tool
        def memory_graph_provenance(intent_id: str) -> dict:
            "Cross-concern provenance for an intent — one graph traversal."
            return mem.provenance(intent_id)

        return mcp
