# Phase 7: Domain handler completion (music + novel + agentic)

This phase completes the feature surface across the five handler-bearing domains (`music`, `novel`, `jules`, `context`, `shared`) plus the `agentic` skill-only domain, per [Plan/harness/VOCABULARY.md](../harness/VOCABULARY.md) §4 and the vision in [Plan/000-overview.md](../000-overview.md) §4. Phase 7's *new work* lands in `novel` + `agentic` + `shared`; the other handler-bearing domains are touched only via cross-cutting envelope/registration conformance.

The scope weaves together five integrated specifications:
- **Spec 014 (PR #108, Merged):** Novel gates and revision scaffolding.
- **Spec 015:** The novel skills catalogue, porting and building 28 skills isomorphic to the music side.
- **Spec 016:** Agentic handlers and skills, establishing 32 tools for spec-driven development.
- **Spec 018:** Overrides and config migration, establishing cross-project preferences cleanly apart from project data.
- **Spec 021:** The novel prompt-builder family, providing 10 specialized, repeatable prompt generation tools.

**Layout & levers:** Phase 7 handlers follow the current **Harness Path A** layout under `servers/agency-mcp/src/agency_mcp/handlers/<domain>/` and adopt the Path A source levers where they exist — Lever L-α (unified `register(mcp)`) and Lever L-β (`@domain_tool(domain="X")` decorator). Future **Harness Path B** ([Plan/harness/restructure/spec.md](../harness/restructure/spec.md)) re-homes these under `domains/<domain>/handlers/` behind a `Domain` base class; Phase 7 is structured so that move is a `git mv`, not a rewrite. See [Plan/harness/design.md](../harness/design.md) §11.2.

**Envelope contract:** Every Phase 7 handler tool returns the **shared ToolResult envelope** from Phase 1 Spec 130 (cross-reference, not a new requirement) — enforced by the `phase-7.shared-toolresult-envelope` acceptance scenario.

**Token-budget win:** Feature completeness across the five handler-bearing domains without bloating the context window, utilizing Code Mode discovery and schema deferral for heavy tools.
