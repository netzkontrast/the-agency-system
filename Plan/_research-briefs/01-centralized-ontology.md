---
type: research-brief
status: dispatched
slug: centralized-ontology
summary: "Jules research brief — design a centralized ontology (frontmatter + Pandoc SUBDOC + Python templating) that unifies music/novel/jules/agentic/shared/scaffold domains, taking inspiration from netzkontrast/agency PR #129's 12-type ontology + 3-mode placement model + auto-generated readmes. Output: findings doc + draft Plan Spec 122."
dispatched_to: jules
dispatched_at: 2026-05-18
parent_specs: [111, 112, 113]
output_branch: research/centralized-ontology
output_files:
  - Plan/_research/centralized-ontology/findings.md
  - Plan/_research/centralized-ontology/draft-spec.md
---

# Research Brief — Centralized Ontology for Plugin Domains

This is the prompt body dispatched to Jules via `jules-bulk fanout`. It is committed here for audit, traceability, and re-dispatch if the first run yields unsatisfactory output. Edit only via supersession (new brief that references this one).

---

## 1. Goal (one sentence)

Produce a research findings document + a draft Plan spec that defines a **single centralized ontology** (artifact types, L1 + L2 frontmatter schemas, placement modes, edge declarations, auto-generated readmes) which unifies every domain inside the `the-agency-system` Claude Code plugin (music, novel, jules, agentic, shared, scaffold) and dovetails with Context Mode Path B (Specs 111 → 112 → 113).

## 2. Why this matters

Today the plugin's content is governed by **ad-hoc, domain-local conventions**:

- **Music**: tracks have YAML frontmatter (status, explicit, sources, …) validated by `hooks/validate_track.py`; overrides are plain Markdown with no schema; albums have hand-written READMEs.
- **Novel**: works/chapters use a separate `ncp.schema.json` + a 6-gate pre-drafting validator; Dramatica ontology is JSON; craft references are unstructured Markdown.
- **Jules / Agentic**: specs use a documented frontmatter convention (`spec_id`, `slug`, `status`, `owner`, `depends_on`, `affects`, …) but no central registry, no schema, no graph of edges.
- **Skills**: per `Plan/000-overview.md` §2.2 — `type`, `status`, `slug`, `summary`, `created`, `updated` (L1 Vault Core) + `skill_*` namespace (L2) + 5 mandatory body sections + cross-ref linter. **This is the only domain in the plugin where a layered ontology already exists.** It works well; it is the seed of the centralized model.

The cost of this fragmentation:

1. Path B (Spec 111 manifest) has to **invent its own tag taxonomy** because there isn't one (`domain:*`, `kind:*`, `topic:*`, `spec:*`, `slug:*`, `lesson_id:*`) — a centralized ontology would *be* the tag taxonomy.
2. Path B (Spec 112 anchor-triad) returns `{id, title, summary, tags, score}` — a richer ontology lets it return typed, graph-walkable results.
3. Cross-domain queries (e.g. "find every artifact in music + novel + agentic tagged `topic:research-discipline`") are impossible without a shared type/edge model.
4. Auto-generated readmes (proven by agency PR #129 to work) save manual maintenance across ~140 skills + 50 specs + 20 overrides + N tracks/chapters.

## 3. Required reading (in order)

1. **netzkontrast/agency PR #129** — `migration: capture 12-type ontology + ULID + auto-readmes refactor design`. Read these files at `refs/pull/129/head`:
   - `migration/handover.md` — orientation
   - `migration/locks-ratified.md` — the 11 binding decisions
   - `migration/schemas-delta.md` — proposed L1 + L2 schema additions, new edge keys, mode-aware validators
   - `migration/adr-draft.md` — ADR-0013 draft (Twelve-Type Ontology + Three-Mode Placement + ULID + Auto-Readmes)
   - `migration/open-questions.md` — Q1–Q7 (blocking)
2. **netzkontrast/agency `main`** — the *current* operational shape that PR #129 will replace:
   - `maintenance/schemas/` — `l1-vault-core.schema.json` + `l2-<type>.schema.json` per type + `header-ontology.json`
   - `tools/fm/` — frontmatter loader + validator (`tools/fm/validate.py`, `tools/fm/gen_schema_mirror.py`)
   - `tools/_frontmatter.py`, `tools/validate-frontmatter.py`, `tools/check-readme-frontmatter.py`
   - `tools/lint-linkage.py`, `tools/lint-structure.py` — cross-edge consistency
   - `tools/check-narrative-ontology-load.py` — ontology graph loader sanity check
   - `tools/check-audit-graph-consistency.py` — edge graph integrity
3. **the-agency-system Plan/** — what the new ontology must serve:
   - `Plan/000-overview.md` — full plugin architecture (§1 target architecture, §2.1 FastMCP/Code Mode conventions, §2.2 skill best practices, §2.3 plugin specifics)
   - `Plan/111-context-mode-manifest/spec.md` — manifest schema + tag taxonomy + BM25 search
   - `Plan/112-context-anchor-triad/spec.md` — `context_search` / `context_describe` / `context_read` + MCP `Resources`
   - `Plan/113-context-cache-and-subscriptions/spec.md` — watcher + change events + manifest auto-rebuild
   - `Plan/JULES_PROTOCOL.md` §C (skill best practices) and §2 (gates)
4. **External references (WebFetch only — do not clone unless §5 lists it):**
   - Pandoc fenced divs / spans: <https://pandoc.org/MANUAL.html#divs-and-spans>
   - Pandoc filters / panflute: <https://pypi.org/project/panflute/>, <https://pandoc.org/filters.html>
   - python-frontmatter: <https://python-frontmatter.readthedocs.io/>
   - ruamel.yaml (round-trip preserving): <https://yaml.readthedocs.io/>
   - Jinja2: <https://jinja.palletsprojects.com/>
   - Cog (code-gen with embedded Python): <https://cog.readthedocs.io/>
   - JSON-LD primer: <https://json-ld.org/learn.html>
   - SHACL (shape constraints over RDF): <https://www.w3.org/TR/shacl/>
   - JSON Schema 2020-12 composition (`$ref`, `allOf`, `oneOf`, `$defs`): <https://json-schema.org/draft/2020-12/json-schema-core>
   - MCP Resources 2025-06-18: <https://modelcontextprotocol.io/specification/2025-06-18/server/resources>
5. **MUST-NOT read inline** (too large for context window — query via grep/head/wc):
   - `reference/dramatica/` (entire Dramatica ontology, ~300 entries)
   - `state/schema/ncp.schema.json`
   - Skill SKILL.md files in bulk — pick representative samples, do not read all 140

## 4. Source clones

```bash
git clone --depth=1 --branch=main \
  https://github.com/netzkontrast/agency.git \
  ~/work/vendor/agency

# Read-only access to PR #129's branch for the migration/ workspace:
cd ~/work/vendor/agency && git fetch origin pull/129/head:pr-129 && git checkout pr-129 -- migration/
```

Never commit anything from `~/work/vendor/`.

## 5. Output

Two files on a **new branch** `research/centralized-ontology` rooted at `Master`:

### 5.1 `Plan/_research/centralized-ontology/findings.md`

A research report (~600–1200 lines of Markdown). Structure:

1. **Executive summary** (≤300 words) — what to adopt, what to adapt, what to skip.
2. **State of the art**
   - Agency PR #129's 12-type ontology — verbatim type list, mode model, identifier convention, schema layering (L1 / L2 / edges)
   - Existing in-plugin precedent — skill L1+L2 (§2.2), spec frontmatter, ncp schema, music track frontmatter, dramatica ontology shape
   - External: JSON Schema composition, JSON-LD, SHACL, Pandoc divs, Jinja2/Cog
3. **Mapping** — for every plugin domain (music, novel, jules, agentic, shared, scaffold), enumerate the artifact kinds that exist today and propose the centralized `type:` value each maps to. Include a table.
4. **Proposed centralized ontology**
   - The N-type enum (start from agency's 12, add/remove as needed for this plugin's domains — e.g. plugin may also need `track`, `album`, `chapter`, `work`, `override`, `lesson`, `reference`, `ontology-entry`, `prompt-builder`)
   - L1 Vault Core schema (`l1-vault-core.schema.json`)
   - L2 per-type schemas (one per type, namespaced `<type>_*`)
   - `header-ontology.json` shape: edge keys, cardinality, forward/reverse declaration
   - Three placement modes (STANDALONE / SUBFILE / SUBDOC) — when to use each; for SUBDOC, propose Pandoc fenced-div syntax verbatim (e.g. `::: {.spec id="111.1"} … :::`)
   - Identifier convention (slug vs ULID per-type)
   - Auto-readme renderer contract (`l2-readme.schema.json`-equivalent + Jinja2 template per type)
5. **Path B integration** — concrete bindings:
   - How L1 + L2 frontmatter populates Spec 111's `ContextManifest` entry fields (`id`, `title`, `summary`, `tags`, `views`, `mime`, …)
   - How edges (`header-ontology.json`) extend Spec 112's `context_describe` response with `neighbours: {…}`
   - How a single source-of-truth schema lets Spec 113's watcher detect ontology violations on file change (not just sha256 drift)
6. **Migration strategy** — non-destructive path from today's heterogeneous conventions to the centralized ontology. Archive-first per agency PR #129's pattern. Use **L1-first** sequencing: ship L1 schema + frontmatter linter, then per-type L2 schemas one domain at a time.
7. **Tooling implications** — what new tooling (separate from validators in Brief 2): an `agency-system-ontology` CLI? A pre-commit hook? A `make ontology-check`?
8. **Open questions** — analogous to PR #129's Q1–Q7 — what blocks promotion to a ratified Plan spec?
9. **Risks & costs**
10. **References** — every URL, file path, commit SHA cited.

### 5.2 `Plan/_research/centralized-ontology/draft-spec.md`

A draft spec following the exact template of `Plan/111-context-mode-manifest/spec.md` (read 111 as the canonical template):

- Frontmatter: `spec_id: 122` (next free slot per `Plan/000-overview.md` §3 — last used spec is 121), `slug: centralized-ontology`, `status: draft`, `owner: jules` (the implementer; this is research output), `depends_on: [111]` (manifest needs frontmatter to read), `affects: [<file paths>]`, `domain: cross`, `wave: D`.
- Required sections: Why · Done When · Source clones · Files (Create / Modify / Delete) · Approach (Gates 1–4 from JULES_PROTOCOL.md §2) · Acceptance (Gherkin, ≥ 5 scenarios) · Out of scope · References.
- Use **RFC-2119 / BCP-14 keywords** in Done When and Approach (MUST / SHOULD / MAY) per the `spec-skill` skill convention.
- Gherkin acceptance: cover at minimum (a) L1 schema validates a representative sample from each domain, (b) edge linter detects a broken edge, (c) auto-readme renderer is byte-identical on second run, (d) a Path B `context_search` returns ontology-typed results, (e) a missing required L2 field fails CI.

## 6. Acceptance — when is this brief "done"?

- [ ] `Plan/_research/centralized-ontology/findings.md` exists, ≥ 600 lines, every required-reading file in §3 is cited at least once with line number or section anchor.
- [ ] `Plan/_research/centralized-ontology/draft-spec.md` exists, follows the Spec 111 template, lints clean against any frontmatter checker that runs on the repo.
- [ ] PR opened from `research/centralized-ontology` to `Master`, body includes the Confidence + TDD + Evidence + Self-Review gates per `Plan/JULES_PROTOCOL.md`.
- [ ] **No code changes** outside `Plan/_research/centralized-ontology/`. Research-only.
- [ ] Vendor source under `~/work/vendor/agency/` is not committed.

## 7. Anti-patterns (Jules MUST NOT)

- Inline-paste large blobs (Dramatica ontology, full skill SKILL.md, vendor sources) into findings.md or draft-spec.md — cite by path + line, do not embed.
- Propose new file layouts under `servers/agency-mcp/` — that's Brief 2's territory. This brief is **data shape only**.
- Modify any file outside `Plan/_research/centralized-ontology/`.
- Adopt agency's 12-type enum verbatim without justifying which types this plugin's domains actually need. (For example: this plugin probably needs `track` + `album` + `chapter` + `work` that agency does not.)
- Skip the open-questions section — explicitly enumerate what you could not resolve.

## 8. Estimated effort

1 Jules session, ~3–5 hours wall-clock. Comparable to the existing `jules-research-3/4/5` outputs already on Master.
