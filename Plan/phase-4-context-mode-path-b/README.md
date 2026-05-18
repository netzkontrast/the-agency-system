# Phase 4: Context Mode Path B — document manifest

This phase implements **Context Mode Path B** as defined in [Plan 000 — Master Overview](../000-overview.md) §4. It solves the token-budget problem of reading large specifications, vendor documents, and lessons learned by moving them from eager inclusion to a deferred, searchable manifest pattern (mirroring the FastMCP CodeMode design). The canonical naming for "Context Mode Path A/B" vs. "Harness Path A/B" lives in [`Plan/harness/VOCABULARY.md`](../harness/VOCABULARY.md) §6 — always use the qualified form.

**Scope:**
- **Spec 111:** Builds the foundational JSON context manifest. The schema is **shared with Phase 5 (Wave D ontology graph)** — the `graph_id` field is the bridge between the manifest entry and the graph node, per [`Plan/000-overview.md`](../000-overview.md) §1 ("graph-based context").
- **Spec 112 (merged PR #104):** Consumes the manifest via the `context_search` / `context_describe` / `context_read` anchor triad. This triad is a **per-domain instance of the four-verb contract** (`VOCABULARY.md` §3) at the `context` domain; the L1 harness invokes it directly via `call_tool(mcp_instance, "context_search", {...})`.
- **Spec 113 (merged PR #113):** Adds caching and change-subscription notifications.
- **Spec 108-stub:** Formally deprecates the alternative **Context Mode Path A** (the rejected `mksglu/context-mode` plugin adapter) in favour of this native implementation.

**Token-Budget Win:**
By cataloguing the corpus and exposing it via tools, ≥ 200 KB of preemptively-inlined documents are converted into an on-demand resource, ensuring the server's initial boot context remains below 500 tokens while providing agents with structured search over `domain:* / kind:* / topic:*` taxonomies.
