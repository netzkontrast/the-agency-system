# AGENTS.md — running the agency engine from bash only

This file is for **bash-only agents** (Jules, Codex, any LLM with a shell and no
MCP client / no Skill loader). You drive the engine with the **same contract** an
MCP client uses — **code-mode** — over a small CLI. No MCP, no skills, no special
integration. The isomorphism is proven in `tests/test_seed.py::test_isomorphism_mcp_equals_bash_cli`.

## Setup (once)

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt   # graphqlite + fastmcp
```

## The contract: code-mode (three commands)

State lives in one graph file you pass as `--db <path>` (it persists across calls).

```bash
# 1. discover what tools exist
python -m agency_seed.cli --db graph.db search "syllables count"

# 2. get a tool's schema (params + returns)
python -m agency_seed.cli --db graph.db get-schema capability_syllables_count

# 3. execute: write Python that chains tools and RETURNS ONLY A DELTA
python -m agency_seed.cli --db graph.db execute --code '
r = await call_tool("capability_syllables_count", {"text": "fix the failing auth test", "intent_id": "intent:abc"})
return r["result"] if isinstance(r, dict) and "result" in r else r
'
# ...or pipe the code in on stdin:
echo 'return await call_tool("memory_graph_provenance", {"intent_id": "intent:abc"})' \
  | python -m agency_seed.cli --db graph.db execute
```

Inside `execute`, `await call_tool(name, params)` is in scope and `return` yields
the result. Every command prints **one JSON document** to stdout.

## The rules (why it's token-efficient)

- **Chain tools inside one `execute` block.** Intermediate results stay in the
  sandbox; only what you `return` crosses back to you. Filter/aggregate before
  returning — return a small delta, never a dump.
- **Discover, don't guess:** `search` to find tools, `get-schema` before you call
  one. The full tool list is never loaded into your context.
- **State is the graph.** Everything you do is recorded as nodes + edges in
  `--db`; ask `memory_graph_provenance` to see what served an intent.

## Why this exists

`agency` exposes one engine three isomorphic ways — MCP tools, Skills, and this
bash CLI. A bash-only agent is therefore a first-class participant: you run the
*same* code-mode contract, against the *same* graph, with the *same* results as
any MCP client. That is what lets Jules (which has only a shell) drive the engine.
