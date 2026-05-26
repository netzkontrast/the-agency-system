"""Bash-callable engine — the L3 layer of the harness-in-harness ladder.

A bash-only agent (Jules, Codex, a raw LLM with a shell) has no MCP client and no
Skill loader. This CLI exposes the engine's ONE contract — **code-mode** — over
argv/stdin/stdout, against a PERSISTED graph (`--db`), so state survives across
separate invocations. It drives the very same code-mode surface
(`search` / `get_schema` / `execute`) the MCP transport exposes, so bash and MCP
are isomorphic by construction: same engine, same contract, same results.

    python -m agency.cli --db graph.db search "lint skill"
    python -m agency.cli --db graph.db get-schema capability_plugin_lint_skill
    python -m agency.cli --db graph.db execute --code 'return await call_tool("capability_plugin_lint_skill", {"name": "Bad Name", "description": "does stuff", "intent_id": "intent:abc"})'
    echo 'return await call_tool(...)' | python -m agency.cli --db graph.db execute

Every command prints a single JSON document to stdout (token-safe, scriptable).
The agent writes CODE that chains tools in-sandbox and returns only a delta — no
flat tool list, no four-verb surface. Code-mode is the contract.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys

from .engine import Engine


def _structured(result):
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


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="agency", description="bash-callable agency engine (code-mode is the contract)")
    p.add_argument("--db", required=True, help="path to the persisted graph database")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="discover tools/capabilities")
    s.add_argument("query")
    g = sub.add_parser("get-schema", help="get the schema of one or more tools")
    g.add_argument("tools", nargs="+")
    x = sub.add_parser("execute", help="run a code block that chains tools; returns a delta")
    x.add_argument("--code", default=None, help="code to run (else read from stdin)")
    i = sub.add_parser("intent", help="capture + confirm an Intent; prints its id")
    i.add_argument("--purpose", required=True)
    i.add_argument("--deliverable", required=True)
    i.add_argument("--acceptance", required=True)   # ontology requires it (non-empty)
    args = p.parse_args(argv)

    # `intent` is the one verb that bootstraps state without an existing intent,
    # so a bash-only agent is fully self-sufficient (Jules review PR #175, finding #3).
    if args.cmd == "intent":
        engine = Engine(args.db)
        try:
            iid = engine.intent.capture(args.purpose, args.deliverable, args.acceptance)
            engine.intent.confirm(iid)
        finally:
            engine.memory.close()
        print(json.dumps({"intent_id": iid}))
        return 0

    if args.cmd == "search":
        name, params = "search", {"query": args.query}
    elif args.cmd == "get-schema":
        name, params = "get_schema", {"tools": args.tools}
    else:  # execute
        code = args.code if args.code is not None else sys.stdin.read()
        name, params = "execute", {"code": code}

    engine = Engine(args.db)
    mcp = engine.build_mcp(codemode=True)
    try:
        out = asyncio.run(mcp.call_tool(name, params))
    finally:
        engine.memory.close()
    print(json.dumps(_structured(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
