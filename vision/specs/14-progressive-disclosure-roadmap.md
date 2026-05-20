---
slug: vision-progressive-disclosure-roadmap
type: roadmap
status: roadmap
owner: claude
created: 2026-05-20
updated: 2026-05-20
summary: Roadmap for the deferred harness levers (L-δ, L-ε, L-ζ, L-η) and the progressive-disclosure 4-tier ladder. None of these are active implementation; they are sequenced, dependency-aware, and not yet scheduled. The 2-tier baseline (list + describe) is active in vision/specs/10-harness-ladder.md §5.6; the 4-tier expansion lives here.
depends_on:
  - vision/specs/10-harness-ladder.md
  - vision/specs/12-vocabulary.md
referenced_by:
  - vision/specs/10-harness-ladder.md
supersedes:
  - Plan/023-harness-in-harness/spec.md
---

# Spec 14 — Progressive Disclosure Roadmap

## 1. Prior-art survey research epic

**Lever**: N/A (Research Epic)
**Description**: Survey existing tools that expose an MCP daemon over a transport plus a thin CLI for external agents (e.g. `mcp dev`, `fastmcp dev`, `mcp-cli` npm package, Continue, Cursor, Cline, smol-tool).
**Motivation**: To map daemon-vs-stateless architectures, transport layers (stdio/HTTP/SSE/WebSocket/ZeroMQ), CLI ergonomics, and licenses, informing our harness-in-harness daemon and CLI.
**Dependencies**: vision/specs/10-harness-ladder.md
**Status**: roadmap
**Anchor**: Plan/023-harness-in-harness/spec.md item 1

## 2. L-δ — SKILL.md required-base schema

**Lever**: L-δ
**Description**: Skill frontmatter validation schema.
**Motivation**: Enforces required metadata in SKILL.md files (e.g., author, domain, summary) to ensure discovery commands work robustly.
**Dependencies**: none
**Status**: roadmap
**Anchor**: Plan/harness/design.md §11.5 row L-δ

## 3. L-ε — Stateful tools (`requires_state` flag)

**Lever**: L-ε
**Description**: Stateful-tool refactor (idempotent or `requires_state` metadata).
**Motivation**: Enables automatic cache warming (`DomainState.warm()`) and ensures state-dependent tools declare their prerequisites explicitly.
**Dependencies**: none
**Status**: roadmap
**Anchor**: Plan/harness/design.md §11.5 row L-ε

## 4. L-ζ — Binary envelope standardisation

**Lever**: L-ζ
**Description**: Binary-payload envelope standardisation. **Important distinction**: This is NOT the spec 02 `data.artefact_ref` overflow mechanism (which is already canon for handling large JSON payloads). L-ζ is about standardising a binary-safe wire format for the MCP envelope itself, enabling tools to stream or return raw binary data without Base64 encoding overhead in the wire JSON.
**Motivation**: Improves performance and memory efficiency for tools dealing with audio, images, or large binary streams.
**Dependencies**: none
**Status**: roadmap
**Anchor**: Plan/harness/design.md §11.5 row L-ζ

## 5. L-η — Tool-only domains formal flag

**Lever**: L-η
**Description**: Skill back-fill / formal "tool-only domain" rule for context/novel/shared.
**Motivation**: Allows domains to explicitly declare they have no skills (`tool_only=True`), preventing missing-directory errors and optimizing the skill discovery process.
**Dependencies**: none
**Status**: roadmap
**Anchor**: Plan/harness/design.md §11.5 row L-η

## 6. Progressive disclosure — 4-tier ladder

**Lever**: N/A (Progressive Disclosure)
**Description**: The full 4-tier ladder for skill and tool discovery.
(1) `list` returns name+summary only.
(2) `describe` adds parameter schema.
(3) `list_skills` returns slug+row+phase.
(4) tier-4 detail still TBD per Plan/023.
**Motivation**: Prevents context-window blowouts when exploring large domains.
**Dependencies**: vision/specs/10-harness-ladder.md
**Status**: roadmap
**Anchor**: Plan/023-harness-in-harness/spec.md item 4. (Note: Cross-reference `vision/specs/10-harness-ladder.md` §5.6 for the active 2-tier baseline).