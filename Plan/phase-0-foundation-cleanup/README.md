# Phase 0: Foundation cleanup

This phase focuses on clearing legacy artefacts and standardising the orchestrator foundations, unblocking Phase 1 of the agency system refactor. It composes two core specifications:

- **Spec 020 (extended):** Deprecates and removes `jules-plugin/`, completing the unification of the workspace and standardising the **four user-facing domain documentation files** at `docs/domain/{music,novel,jules,agentic}.md` (per `Plan/harness/VOCABULARY.md` §4.1; the canonical handler-bearing domain count is five — `music`, `novel`, `jules`, `context`, `shared` — plus the `agentic` skill-only domain, but `context` and `shared` are infrastructural and do not warrant standalone user guides).
- **Spec 099 (stub only):** Authors the orchestration-improvements stub plus lint scripts for missing `affects:` clauses. The full Spec 099 (§2.2 skill-schema lockdown and token-discipline enforcement across the orchestrator surface) lands in **Phase 8**.

**What this unblocks downstream:**

- Rehoming `bin/jules-bulk` and `bin/jules-dev-install` to repo root establishes `bin/` as the canonical home for the **L3 CLI binary `bin/agency`** that ships in Phase 8 (see `Plan/harness/VOCABULARY.md` §2).
- Removing `jules-plugin/` finishes the **"one plugin, one MCP server"** invariant from the north star (`Plan/000-overview.md` §1; `Plan/harness/VOCABULARY.md` §1) — jules tools already migrated to `handlers/jules/` under the unified `agency-mcp` server.

**Token-budget win:** Removing the duplicate `jules-plugin/` directory and shifting orchestrator skills to `skills/agentic/` reduces index bloat and contextual overhead, keeping the unified plugin boot context within the cold-start budget of **< 500 tokens** (`Plan/000-overview.md` §5).

Canonical naming for layers, verbs, domains, and paths used by this phase: see [`Plan/harness/VOCABULARY.md`](../harness/VOCABULARY.md). Broader dependency map: [`Plan/000-overview.md` §4](../000-overview.md).
