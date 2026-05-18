---
type: note
status: complete
slug: 2026-05-18-research-1-mcp-findings
summary: Research Agent 1 (MCP + Code Mode + tool-handler integration) audit findings, slots 130-131.
created: 2026-05-18
updated: 2026-05-18
---

# Research Agent 1 — MCP + Code Mode + tool-handler integration audit (2026-05-18)

## What I reviewed

- `Plan/000-overview.md` §2.1 (Code Mode + MCP conventions, all 11 sub-bullets).
- Existing token-efficiency + Code Mode specs: 008 (registry), 022 (dev install), 103 (view/fields), 104 (anchor triad), 105 (TOON), 106 (gh summary wrappers), 107 (cache breakpoint), 108 (context-mode plugin adopt), 111 / 112 / 113 (context-mode build).
- Operational specs: 099 (orchestration improvements), 100 (session-log-mcp), 101 (jules MCP additions), 102 (rebase policy).
- Shipped agency-mcp source: `servers/agency-mcp/src/agency_mcp/server.py`, `lib/codemode/registry.py`, `lib/codemode/deferred_loader.py`, `codemode/manifest.json` (110 entries — 4 eager, 102 deferred, 4 background), `handlers/shared/config.py`, `handlers/shared/reference.py`, `handlers/shared/session.py`, `handlers/music/__init__.py` + `core.py`, `tools/validate_help_completeness.py`.
- `Plan/_lessons-learned/14-token-consumption-postmortem.md` (the inciting incident for the 103-107 wave).
- `netzkontrast/agency` repo at `/home/user/agency/`: `Agency-System/backend/agency_backend/mcp_server.py` (10-tool FastMCP server, no Code Mode, no envelope, no manifest, raw dict/list returns), `tools/`, top-level `AGENTS.md` / `RESEARCH.md` / `TASK.md` (MCP mentions are mostly Serena/GitHub references, not their own MCP design).
- Superpowers marketplace at `/root/.claude/plugins/cache/superpowers-marketplace/`: `private-journal-mcp/1.2.0/src/server.ts` (raw `@modelcontextprotocol/sdk` server, hand-written `ListToolsRequestSchema` / `CallToolRequestSchema`, `content[0].text` plain-text responses — a different paradigm from FastMCP); the `superpowers/5.1.0/` plugin is skills + hooks only, no MCP server of its own.

## Findings table

| # | Idea | Status |
|---|------|--------|
| 1 | Shared plugin-wide `ToolResult` Pydantic envelope + conformance gate | **Became Spec 130** |
| 2 | Code Mode manifest coverage CI lint (drift detector) | **Became Spec 131** |
| 3 | Domain-filterable `agency_tool_search(domain=...)` for the triad | **Dropped — overlaps Spec 104** (104.2 acceptance scenario already requires the `domain` filter) |
| 4 | Tool-error structured response (`ok=false`, `error.code`, `error.message`) | **Folded into Spec 130** — `ToolResult.error: ErrorInfo \| None` covers it; `wrap_envelope` catches `Exception` and maps to `ok=False` |
| 5 | MCP `Resources` primitive integration (`@mcp.resource`, `resources/subscribe`) | **Dropped — overlaps Spec 112** (112 publishes each context entry as `context://<id>` MCP Resource) and **Spec 113** (resources/subscribe + notifications/resources/updated wiring) |
| 6 | Subagent-dispatched MCP wrappers for token-heavy reads | **Dropped — overlaps Spec 106** (gh_pr_summary / gh_issue_summary / gh_review_summary use this exact pattern; 106 is the canonical Wave-C reference) |
| 7 | Raw MCP SDK fallback if FastMCP becomes unavailable | **Dropped — out of scope** (private-journal-mcp uses raw SDK but that's a 5-tool server; agency-mcp's 110+ tool surface is FastMCP-native by Spec 001's foundational decision) |
| 8 | `defer_schema=True` runtime-flag plumbing on `@mcp.tool` | **Dropped — superseded** (Spec 008's `deferred_loader.py` documents that FastMCP 3.3.1 has NO `defer_schema=True` kwarg; the CodeMode `transform_tools` hook hides deferred tools; intent is recorded on `fn._codemode_classification`. Adding a stub kwarg would be cosmetic) |

## Spec decisions

- **Slot 130** → `shared-toolresult-envelope` — Pydantic `ToolResult` + `ErrorInfo` models, `wrap_envelope` decorator (sync + async, exception-capturing, `functools.wraps`-preserving), migration of `handlers/shared/{config,reference,session}.py` as the canonical template, integration test enumerating every `domain:shared` tool. Wave C, cross-domain, depends on 008 + 009.
- **Slot 131** → `manifest-coverage-lint` — `tools/check_codemode_manifest.py` script + `lib/codemode/registry.manifest_diff()` helper + GitHub Actions workflow scoped to MCP paths. Catches manifest drift in CI before it surfaces as a boot-time `ValueError` on Master. Wave C, cross-domain, depends on 008.

Both specs declared `status: draft` per the protocol — human review required before flipping to `ready`.

## Noteworthy items that do NOT warrant a spec but should be on the orchestrator's radar

1. **agency-mcp's `_AnchorAwareCodeMode` subclass (`server.py:18-39`) is a load-bearing patch around FastMCP 3.3.x's stock `CodeMode.transform_tools` which returns *only* `[*discovery, execute]`** — hiding every anchor. The current workaround merges anchor tools back into the transform output. If FastMCP upstream changes this behaviour (e.g. accepts a native anchor list), Spec 008's subclass becomes dead code. Worth a one-line tracking note in `Plan/_lessons-learned/`.

2. **Spec 016's `_envelope.py` is scoped to `handlers/agentic/`** — if Spec 016 lands BEFORE Spec 130, the agentic envelope ships first and Spec 130 must hoist it (one extra migration step). If Spec 130 lands first (recommended), Spec 016 imports from `lib/envelope/` cleanly. Dispatch order matters; orchestrator should prefer 130 → 016 over 016 → 130.

3. **The sibling `netzkontrast/agency` MCP server (`Agency-System/backend/agency_backend/mcp_server.py`) returns raw `list[dict]` / `dict` from every tool** — no envelope, no `ok` flag, no warnings accumulator. This is the comparison reference cited in Spec 130's source clones — it shows the failure mode this plugin's §2.1 #9 envelope discipline prevents. NOT a thing to import; a thing to point at.

4. **`mcp._tools` is a private FastMCP attribute that both Spec 008 (registry validation), Spec 104 (anchor triad), Spec 130 (envelope conformance test), and Spec 131 (manifest coverage lint) depend on.** If FastMCP changes this surface (e.g. renames to `mcp.tools` or makes it a method), four specs need a coordinated patch. Worth marking in `Plan/SOURCES.md` as a FastMCP version-pin justification.

5. **Private-journal-mcp's response shape (`content[0].text` plain-text formatted strings, not JSON) is the MCP SDK's default convention** — FastMCP's default is structured JSON via Pydantic. The two paradigms are incompatible; agency-mcp is firmly on the FastMCP side. No action needed; cited for situational awareness.

6. **The `Plan/_lint/` directory referenced by Specs 099 and 102 (`Plan/_lint/check_affects.py`, `Plan/_lint/check_install_consistency.py`, `Plan/_lint/check_rebase_status.py`) does not yet exist on Master.** Spec 131's GitHub Actions workflow path doesn't depend on it, but if Spec 099 ships its lint scripts first, the two efforts should converge on a single `Plan/_lint/` (or `tools/lint/`) directory convention.

## Confidence

Both new specs cite real file paths (verified via Read/grep), the canonical spec format from `Plan/022-dev-mode-install/spec.md`, every Gherkin scenario references a testable artefact, and every Done-When item is mechanically verifiable. Source clones declared as `[]` because both specs vendor no external code — they extend the existing tree.