# Research 01 — FastMCP in-memory transport

> **Question.** Can the L1 harness invoke `agency-mcp`'s 114 tools without spinning up an stdio subprocess?
> **Answer.** Yes — `mcp.call_tool(name, params)` on the FastMCP instance IS the in-memory transport. The pattern is already used in the repo at `tests/integration/test_context_anchor_triad.py`.

## 1. FastMCP's invocation surface

`fastmcp.FastMCP` exposes three relevant async methods for in-process calls:

| Method | Purpose | Used by |
|---|---|---|
| `mcp.list_tools()` | Enumerate registered tools as `Tool` objects with `.name`, `.tags`, `.description` | `tests/integration/test_context_anchor_triad.py:9` |
| `mcp.call_tool(name: str, params: dict)` | Invoke a tool's handler. Returns a `ToolResult` envelope. | `tests/integration/test_context_anchor_triad.py:14, 24, 30, 35` |
| `mcp.list_resources()` | Enumerate registered MCP resources (separate from tools) | `tests/integration/test_context_anchor_triad.py:43` |

The handler function is **not** directly accessible as `mcp.tools[name].fn` — the parallel-agent map (Plan/harness coordination, MCP+codemode-surface agent §5) noted this and the L1 design respects it. The supported in-memory path is `await mcp.call_tool(...)`.

### 1.1 Lower-level access (used in one place)

`tests/unit/jules/test_handlers_smoke.py:10` uses `mcp._local_provider.list_tools()` to bypass the public API. This is undocumented and the underscore signals "do not depend on this". L1 deliberately uses `mcp.list_tools()` (public) instead.

## 2. The wire-format on the return path

`ToolResult` is an envelope; the JSON body lives at `result.content[0].text`. From `tests/integration/test_context_anchor_triad.py:21` verbatim:

```python
search_results = await mcp.call_tool("context_search", {"query": "dramatica ontology", "limit": 5})
# The result from fastmcp.call_tool is a ToolResult envelope with `content[0].text`
search_results_json = json.loads(search_results.content[0].text)
```

L1's `call_tool` wrapper unwraps this envelope so callers see plain dicts. Errors during unwrap (non-JSON body, missing `.content[0]`, etc.) raise `HarnessError` to make debugging cheap.

## 3. Boot cost and singleton justification

`create_mcp()` ([`servers/agency-mcp/src/agency_mcp/server.py:99-106`](../../servers/agency-mcp/src/agency_mcp/server.py)) does the following on every call:

1. Instantiate `FastMCP("agency-system", ...)` with the `_AnchorAwareCodeMode` transform.
2. Invoke `register_all(mcp)` (`server.py:60-85`), which:
   - Registers ~8 context anchor tools.
   - Initialises `StateCache` for music (instantiates `MusicIndexer`, loads disk state).
   - Registers ~8 shared tools, ~83 novel tools, ~82 music tools, ~28 jules tools, ~4 context tools.
3. `register_context_handlers` starts a daemon thread `ContextWatcher` ([`lib/codemode/context_watcher.py:17-168`](../../servers/agency-mcp/src/agency_mcp/lib/codemode/context_watcher.py)) polling Plan/_lessons-learned/_overrides/_reference paths every 5s.

A per-test boot would cost: handler-registration walk + StateCache disk reads + watcher thread spawn. Booting once per pytest session via `@lru_cache(maxsize=1)` keeps the cost amortised and avoids watcher-thread leaks across tests.

The L1 module's `harness_mcp()` is `lru_cache`d for exactly this reason. A `pytest_sessionfinish` hook (later, when the harness lands) calls `watcher.stop()` to keep the test process clean.

## 4. Existing handler-isolated pattern

`tests/unit/jules/test_handlers_smoke.py:7-10` shows the handler-isolated pattern (used today for the jules-tools count assertion):

```python
mcp = FastMCP("test-jules")
register_jules_handlers(mcp)
tools = asyncio.run(mcp._local_provider.list_tools())
```

L1's `list_tools` verb gives the **full plugin** view (all 114 tools) by going through `create_mcp()`. For per-domain testing, the existing `register_<domain>_handlers(mcp)` pattern is preserved and orthogonal — L1 layers on top, it does not replace handler-isolated tests.

## 5. Why this works in CI / sandboxed envs

- No stdio subprocess → no FIFO / socket setup.
- No network → no port binding, no firewall concerns.
- Same Python process → tracebacks point at the real handler code, not at a remote process.
- pytest can collect coverage on handler code through the harness invocation.

## 6. Counter-evidence — what we tested

`python -c "from fastmcp import FastMCP, Client; ..."` fails with `ModuleNotFoundError: No module named 'fastmcp'` in the current sandbox before `bin/agency-dev-install` runs. After `bin/agency-dev-install` (verified by Dev-Install audit agent on this branch), `from agency_mcp.server import create_mcp` succeeds and `create_mcp()` returns `FastMCP('agency-system')`. The L1 harness assumes the install ran — `tests/_harness/__init__.py` will raise a clear error message if `agency_mcp` is unimportable, pointing at `bin/agency-dev-install`.

## References

- FastMCP docs — [Client transports / in-memory](https://gofastmcp.com/clients/transports#in-memory-transport)
- FastMCP docs — [Server overview](https://gofastmcp.com/servers/fastmcp)
- `servers/agency-mcp/src/agency_mcp/server.py:60-106` — boot sequence
- `tests/integration/test_context_anchor_triad.py:1-49` — canonical in-memory pattern
- `tests/unit/jules/test_handlers_smoke.py:1-26` — handler-isolated pattern
