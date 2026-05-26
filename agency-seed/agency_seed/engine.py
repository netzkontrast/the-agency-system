"""Engine — one FastMCP server + one graph. The four-verb contract (list_tools /
call_tool are MCP-native; list_skills / dispatch_skill are surfaced as tools,
since MCP has no skill RPC). Optional code-mode transform hides the raw tools
behind search / get_schema / execute (the −98%-token pattern), exactly as the
local jules-plugin does.

Tool names are MCP-conformant `<concept>_<capability>_<verb>` (underscores, no
dots, ≤64) — the client injects the `mcp__` prefix.
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
from .intent import Intent
from .lifecycle import Lifecycle
from .memory import Memory


class Engine:
    def __init__(self, path: str):
        self.memory = Memory(path)
        self.intent = Intent(self.memory)
        self.lifecycle = Lifecycle(self.memory)
        self.registry = Registry()
        self.registry.register(syllables_capability)
        self.registry.register(jules_capability)

    def build_mcp(self, codemode: bool = False) -> FastMCP:
        transforms = [CodeMode()] if (codemode and HAVE_CODEMODE) else []
        mcp = FastMCP("agency-seed", transforms=transforms)
        reg, mem = self.registry, self.memory

        @mcp.tool
        def capability_syllables_count(text: str, intent_id: str) -> int:
            "Count syllables (transform); recorded as an Invocation that SERVES the intent."
            result, _ = reg.invoke(mem, intent_id, "syllables", "count", text=text)
            return result

        @mcp.tool
        def capability_jules_patch(spec: str, intent_id: str, agent_id: str, pushed: bool = False) -> dict:
            "jules patch (act); records Invocation BY agent + PRODUCES artefact."
            result, _ = reg.invoke(mem, intent_id, "jules", "patch",
                                   agent_id=agent_id, spec=spec, pushed=pushed)
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

        @mcp.tool
        def agency_list_skills() -> list:
            "Four-verb contract: list capabilities (skills)."
            return reg.names()

        @mcp.tool
        def agency_dispatch_skill(name: str) -> dict:
            "Four-verb contract: dispatch a skill (capability) by name."
            cap = reg.get(name)
            return {"name": cap.name, "home": cap.home, "verbs": list(cap.verbs)}

        return mcp
