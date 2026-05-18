# Phase 7: Domain handler completion (music + novel + agentic)

This phase completes the feature surface for all four domains (music, novel, agentic, shared), fulfilling the vision from [Plan/000-overview.md](../000-overview.md) §4.

The scope weaves together five integrated specifications:
- **Spec 014 (PR #108, Merged):** Novel gates and revision scaffolding.
- **Spec 015:** The novel skills catalogue, porting and building 28 skills isomorphic to the music side.
- **Spec 016:** Agentic handlers and skills, establishing 32 tools for spec-driven development.
- **Spec 018:** Overrides and config migration, establishing cross-project preferences cleanly apart from project data.
- **Spec 021:** The novel prompt-builder family, providing 10 specialized, repeatable prompt generation tools.

**Token-budget win:** Feature completeness across all four domain handlers without bloating the context window, utilizing Code Mode discovery and schema deferral for heavy tools.
