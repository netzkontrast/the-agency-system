# Phase 4: Context Mode (Path B) — document manifest

This phase implements "Path B" for Context Mode as defined in [Plan 000 — Master Overview](../000-overview.md) §4. It solves the token-budget problem of reading large specifications, vendor documents, and lessons learned by moving them from eager inclusion to a deferred, searchable manifest pattern (mirroring the FastMCP CodeMode design).

**Scope:**
- **Spec 111:** Builds the foundational JSON context manifest.
- **Spec 112 (merged PR #104):** Consumes the manifest via the `context_search` / `context_describe` / `context_read` anchor triad.
- **Spec 113 (merged PR #113):** Adds caching and change-subscription notifications.
- **Spec 108-stub:** Formally deprecates the alternative "Path A" (mksglu plugin) in favour of this native implementation.

**Token-Budget Win:**
By cataloguing the corpus and exposing it via tools, ≥ 200 KB of preemptively-inlined documents are converted into an on-demand resource, ensuring the server's initial boot context remains below 500 tokens while providing agents with structured search over `domain:* / kind:* / topic:*` taxonomies.
