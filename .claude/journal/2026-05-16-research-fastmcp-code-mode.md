# Research: FastMCP Code Mode + Caveman (2026-05-16)

## FastMCP Code Mode (the headliner)

- **What**: A FastMCP server *transform* that swaps "one tool call per action" for "model writes a Python snippet that calls tools inside a sandbox".
- **When**: FastMCP 3.1 ("Code to Joy"), released 2026-03-03.
- **Why**: Open-source implementation of Anthropic's Nov-2025 pattern "Code execution with MCP".
- **Docs**: https://gofastmcp.com/servers/transforms/code-mode

### Wire protocol

Standard MCP — no new transport. Code Mode replaces the server's tool surface with three meta-tools: `search`, `get_schema`, `execute`. The LLM calls `execute` with a Python snippet:

```python
a = await call_tool("add", {"x": 3, "y": 4})
b = await call_tool("multiply", {"x": a, "y": 2})
return b
```

### Token economics (real numbers)

- Amazon Ads MCP: **34,000 → ~600 tokens** per workflow.
- Anthropic reference: **150K → 2K (~98.7%)**.
- Cloudflare: 2,500 endpoints in ~1,000 tokens.

### When it HURTS

- Small servers / few tools (upfront listing is cheaper than 3-stage discovery).
- Weaker models (Haiku-4.5-class) made errors before adapting.
- Trivial single-tool calls (overhead exceeds savings).

### Server opt-in (ONE LINE)

```python
from fastmcp import FastMCP
from fastmcp.experimental.transforms.code_mode import CodeMode

mcp = FastMCP("Server", transforms=[CodeMode()])
```

Install: `pip install "fastmcp[code-mode]"`. Existing `@mcp.tool()` decorations need ZERO changes.

### Sandbox

- Runtime: Pydantic's **Monty** (experimental Python sandbox).
- **Restrictions: no filesystem, no network, no pip deps.** Stdlib + injected `call_tool` only.
- Configurable timeouts, memory caps, recursion-depth limits.
- `SandboxProvider` protocol swappable (Docker, remote, etc.).

### Client-side support

**None needed.** Code Mode is invisible on the wire — looks like a server with three tools. Claude Code docs don't mention Code Mode. No `--code-mode` flag, no env var.

## Caveman (the user mentioned it)

- **What**: A Claude Code **skill** (not MCP), https://github.com/JuliusBrussee/caveman, v1.8.2.
- **How**: Instructs the agent to answer in telegraphic fragments — drops articles, pleasantries, problem restatements.
- **Claimed savings**: ~65% output-token reduction across 10 prompts.
- **Realistic savings** (independent review): **4–10% session-wide** — because output is only ~25% of a typical session and reasoning/input tokens are untouched.
- **Bonus**: ships `caveman-shrink` npm — MCP middleware that wraps any MCP server and compresses tool descriptions.

## Combined strategy

- **Code Mode**: attacks tool-result + tool-listing bloat via sandboxed code execution.
- **Caveman**: attacks prose-output bloat via style instructions.
- **caveman-shrink**: attacks tool-description bloat via middleware.

Complementary, not competing. For our refactor:

1. **Code Mode is the big win** (98% in best cases).
2. **Caveman/caveman-shrink** are nice-to-have (single-digit %).
3. The two together could push token cost of a Jules orchestration session from current ~5-10K per turn to a few hundred.
