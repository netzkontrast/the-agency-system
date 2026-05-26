"""Engine — one FastMCP server + one graph.

**Code-mode IS the contract** (lean: no separate four-verb surface). The engine
exposes exactly `search` / `get_schema` / `execute`; the underlying tools
(capabilities, gate, provenance) are discovered via `search` and called from
inside `execute` (`await call_tool(name, params)`). This is the same surface a
bash agent drives via `agency/cli.py` — so MCP and bash are isomorphic by
construction. Tool names are MCP-conformant `capability_<capability>_<verb>`.

**Capabilities are self-registering.** The engine does not hand-wire a tool per
verb. It `discover()`s every `Capability` in the `capabilities/` package
(reflection) and AUTO-WIRES one MCP tool per verb from the verb function's
signature (`inspect.signature`). Adding a capability is adding a file — no
registration code, no per-tool boilerplate. Params named in a verb's `inject`
list (e.g. `client`, `caps`) are supplied by the engine, not the caller.
"""
from __future__ import annotations

import inspect

from fastmcp import Context, FastMCP

try:
    from fastmcp.experimental.transforms.code_mode import CodeMode
    HAVE_CODEMODE = True
except ImportError:  # pragma: no cover
    HAVE_CODEMODE = False

from .capabilities import discover
from .capabilities.jules import RealJulesClient
from .capability import Registry
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
        for cap in discover():                                  # reflection: register by discovery
            self.registry.register(cap)

    def _injectors(self) -> dict:
        """Engine-supplied verb params (the `inject` convention): the boundary
        objects/live state a pure verb shouldn't have to construct itself."""
        reg = self.registry
        return {
            "client": lambda: self.jules_client,
            "caps": lambda: {n: list(reg.get(n).verbs) for n in reg.names()},
        }

    def _wire(self, mcp: FastMCP, cap_name: str, verb: str, spec: dict, injectors: dict) -> None:
        """Auto-wire ONE MCP tool for a capability verb from its fn signature."""
        reg, mem = self.registry, self.memory
        fn, inject = spec["fn"], list(spec.get("inject", []))
        user_params = [p for n, p in inspect.signature(fn).parameters.items() if n not in inject]

        def impl(**kwargs):
            intent_id = kwargs.pop("intent_id")
            agent_id = kwargs.pop("agent_id", "") or None
            for name in inject:
                kwargs[name] = injectors[name]()
            result, _ = reg.invoke(mem, intent_id, cap_name, verb, agent_id=agent_id, **kwargs)
            out = result["result"] if isinstance(result, dict) and "result" in result else result
            return out if isinstance(out, dict) else {"result": out}

        params = []
        for p in user_params:
            ann = p.annotation if p.annotation is not inspect.Parameter.empty else str
            default = p.default if p.default is not inspect.Parameter.empty else inspect.Parameter.empty
            params.append(inspect.Parameter(p.name, inspect.Parameter.KEYWORD_ONLY, annotation=ann, default=default))
        params.append(inspect.Parameter("intent_id", inspect.Parameter.KEYWORD_ONLY, annotation=str))
        params.append(inspect.Parameter("agent_id", inspect.Parameter.KEYWORD_ONLY, annotation=str, default=""))

        impl.__signature__ = inspect.Signature(params)
        impl.__name__ = f"capability_{cap_name}_{verb}"
        impl.__doc__ = (fn.__doc__ or "").strip() or f"{cap_name}.{verb} ({spec['role']})"
        impl.__annotations__ = {p.name: p.annotation for p in params}
        impl.__annotations__["return"] = dict
        mcp.tool(impl)

    def build_mcp(self, codemode: bool = True) -> FastMCP:
        transforms = [CodeMode()] if (codemode and HAVE_CODEMODE) else []
        mcp = FastMCP("agency-seed", transforms=transforms)
        mem = self.memory
        injectors = self._injectors()

        # every capability verb -> one MCP tool, by reflection (no hand-wiring)
        for cap_name in self.registry.names():
            cap = self.registry.get(cap_name)
            for verb, spec in cap.verbs.items():
                self._wire(mcp, cap_name, verb, spec, injectors)

        # engine-substrate tools (not capabilities): a human-in-the-loop gate that
        # needs `ctx.elicit`, and the provenance traversal over the graph.
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
