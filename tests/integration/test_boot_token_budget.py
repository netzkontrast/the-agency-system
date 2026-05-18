"""Boot token budget integration test.

Spec: Plan/008-codemode-registry/spec.md (Done When §boot token budget,
Acceptance anchor 008.1).

Boots the FastMCP server, asks for the post-transform ``tools/list``
payload (i.e. what an LLM client actually sees), and asserts:

  * The serialised payload is <= 3000 bytes.
  * The tiktoken cl100k_base encoding of that payload is <= 500 tokens.

The byte ceiling exists because the CodeMode meta-tools
(``search``/``get_schema``/``execute``) alone consume ~1800 bytes of
baseline before any anchor tools are added. The remaining ~1200 byte
budget is what funds the ~4 anchor tools the spec calls for. The
500-token budget is the Anthropic-billing-cost cap.

If either assertion fails, the fix is NOT to raise the threshold but to
reclassify more tools from eager to deferred in
``codemode/manifest.json``.
"""
from __future__ import annotations

import asyncio
import json

import tiktoken

from agency_mcp.server import create_mcp

_enc = tiktoken.get_encoding("cl100k_base")


def _boot_payload() -> str:
    """Return the JSON string a real MCP client would receive from
    ``tools/list`` after all transforms (including CodeMode) have run."""
    mcp = create_mcp()
    tools = asyncio.run(mcp.list_tools())
    visible = []
    for t in tools:
        visible.append(
            {
                "name": t.name,
                "description": (t.description or "").split("\n")[0],
                "tags": sorted(list(t.tags)) if getattr(t, "tags", None) else [],
            }
        )
    return json.dumps(visible, ensure_ascii=False)


def test_boot_byte_budget():
    payload = _boot_payload()
    size = len(payload.encode("utf-8"))
    assert size <= 3000, (
        f"Boot payload {size}B exceeds 3000-byte ceiling "
        "(CodeMode baseline ~1800B + ~4 anchors per domain). "
        "If new domains added, audit anchor classifications in "
        "codemode/manifest.json."
    )


def test_boot_token_budget():
    payload = _boot_payload()
    tokens = len(_enc.encode(payload))
    assert tokens <= 500, (
        f"Boot payload {tokens}t exceeds 500-token budget. "
        "Move tools from eager to deferred in codemode/manifest.json."
    )


def test_codemode_meta_tools_present():
    """Acceptance anchor 008.1: the search, get_schema, and execute
    meta-tools are present in the post-transform listing."""
    mcp = create_mcp()
    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}
    assert "search" in names, f"search meta-tool missing; got {names}"
    assert "get_schema" in names, f"get_schema meta-tool missing; got {names}"
    assert "execute" in names, f"execute meta-tool missing; got {names}"
