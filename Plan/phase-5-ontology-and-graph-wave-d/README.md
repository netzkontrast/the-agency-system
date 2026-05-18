# Phase 5: Ontology + Graph (Wave D)

This phase implements **Path B (content layer)** from the agency-system architecture, introducing a unified, cross-domain semantic graph. It composes four critical specifications:

- **Spec 122 (centralized ontology):** Defines an 18-type unified schema and edge declarations for artefacts across all domains.
- **Spec 123 (agency-tooling Code Mode):** Ports and types netzkontrast validators into FastMCP tools (`ontology_validate_frontmatter`, etc.) maintaining an eager anchor budget of ≤ 170 tokens.
- **Spec 124 (GraphQLite Code Mode):** Replaces localized state lookups with an in-process EAV SQLite graph mapping, delivering 18 graph algorithms locally.
- **Spec 135 (spec-test anchor traceability):** Enforces a test-coverage lint ensuring every `# anchor: NNN.n` tag corresponds to a pytest scenario.

**Token-budget win:** Cross-domain queries collapse from N file reads to a single Cypher `MATCH`, dramatically reducing context-window exhaustion and keeping tool lists under the `tools/list` < 4 KB baseline.

See [Plan/000-overview.md §4](.../000-overview.md#wave-d--path-b-content-layer-extends-111-113) for the dependency DAG and phase context.