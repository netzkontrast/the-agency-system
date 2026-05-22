# Phase 5: Ontology + Graph (Wave D)

This phase implements **Context Mode Path B (content layer; see [Plan/harness/VOCABULARY.md](../harness/VOCABULARY.md) §6.1)** from the agency-system architecture, introducing a unified, cross-domain semantic graph. It composes four critical specifications:

- **Spec 122 (centralized ontology):** Defines an 18-type unified schema and edge declarations for artefacts across all domains.
- **Spec 123 (agency-tooling Code Mode):** Ports and types netzkontrast validators into FastMCP tools (`ontology_validate_frontmatter`, etc.) maintaining an eager anchor budget of ≤ 170 tokens.
- **Spec 124 (GraphQLite Code Mode):** Replaces localized state lookups with an in-process EAV SQLite graph mapping, delivering 18 graph algorithms locally.
- **Spec 135 (spec-test anchor traceability):** Enforces a test-coverage lint ensuring every `# anchor: NNN.n` tag corresponds to a pytest scenario.

**Token-budget win:** Cross-domain queries collapse from N file reads to a single Cypher `MATCH`, dramatically reducing context-window exhaustion and keeping tool lists under the `tools/list` < 4 KB baseline.

**Manifest schema sharing with Phase 4:** Phase 5 consumes Phase 4's `context_manifest.json` entries via their `graph_id` field, so document discovery (Context Mode Path B) and structural queries (Wave D graph) reinforce each other.

**Forward-compat note (Harness Path B):** The 18-type ontology + `ontology_*` validators are the source-level enforcement of conventions that Harness Path B ([Plan/harness/restructure/spec.md](../harness/restructure/spec.md)) would later centralize in `domains/_base/conventions.py`. Phase 5 ships the cross-domain enforcement; the restructure endgame would co-locate the same conventions with the `Domain` base class.

Canonical naming reference for this phase: [Plan/harness/VOCABULARY.md](../harness/VOCABULARY.md).

See [Plan/000-overview.md §4](../000-overview.md#wave-d--path-b-content-layer-extends-111-113) for the dependency DAG and phase context.