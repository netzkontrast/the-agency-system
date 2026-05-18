# Phase 0: Foundation cleanup

This phase focuses on clearing legacy artefacts and standardising the orchestrator foundations, unblocking Phase 1 of the agency system refactor. It composes two core specifications:

- **Spec 020 (extended):** Deprecates and removes `jules-plugin/`, completing the unification of the workspace and standardising the four domain docs.
- **Spec 099 (stub):** Introduces Jules orchestration improvements, locking down the §2.2 skill schemas, adding lint scripts for missing `affects:` clauses, and enforcing token discipline across the orchestrator surface.

**Token-budget win:** By removing the duplicate `jules-plugin/` directory and shifting orchestrator skills to the new `skills/agentic/` location, we significantly reduce index bloat and contextual overhead. The unified plugin boot context sits firmly at 210 tokens, while removing thousands of redundant lines.

See the broader dependency map in [`Plan/000-overview.md` §4](../000-overview.md).
