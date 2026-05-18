---
spec_id: 122
slug: centralized-ontology
status: ready
owner: jules
depends_on: [111, 112, 113]
affects:
  - maintenance/schemas/l1-vault-core.schema.json
  - maintenance/schemas/header-ontology.json
  - maintenance/schemas/l2-readme.schema.json
  - tools/fm/validate.py
  - tools/cli/agency_ontology.py
  - templates/readme.j2
domain: cross
wave: D
estimated_jules_sessions: 1
source-repos: [netzkontrast/agency @ main]
inspired_by: netzkontrast/agency#129
research: Plan/_research/centralized-ontology/findings.md
---

# Spec 122: Centralized Ontology for Plugin Domains

## Why

The `the-agency-system` plugin currently suffers from ad-hoc, localized conventions across its domains (music, novel, jules, agentic). This fragmentation prevents cross-domain querying, complicates validation, and limits the richness of the Context Mode Path B architecture. By adopting a centralized ontology — inspired by `netzkontrast/agency` PR #129 but adapted for our specific domains — we unify metadata, explicitize edge relationships, and unlock automated documentation generation.

## Done When

1. **L1 Vault Core Schema:** `l1-vault-core.schema.json` is defined, supporting an extended enum of types (`task`, `prompt`, `research`, `spec`, `readme`, `note`, `skill`, `adr`, `track`, `album`, `work`, `chapter`, `override`, `lesson`, `reference`, `ontology-entry`, `prompt-builder`, `gherkin`).
2. **Edge Declarations:** `header-ontology.json` is created, defining explicit edge keys, cardinality, and source/target constraints.
3. **Linter Update:** `tools/fm/validate.py` is updated to enforce the new L1 schema across all tracked markdown files.
4. **Auto-Readme Contract:** `l2-readme.schema.json` and a Jinja2 template (`templates/readme.j2`) are implemented to generate readmes from artifact frontmatter.
5. **CLI Tooling:** `tools/cli/agency_ontology.py` is implemented with `lint` and `readme` subcommands.
6. **SUBDOC parser:** Pandoc fenced div extraction uses `markdown-it-py` AST walk (see Open question Q1 below — pinned by this spec).

## Source clones

None required for implementation. All necessary research was completed during the `centralized-ontology` brief phase (see `Plan/_research/centralized-ontology/findings.md`).

## Files

- **Create:** `maintenance/schemas/l1-vault-core.schema.json`
- **Create:** `maintenance/schemas/header-ontology.json`
- **Create:** `maintenance/schemas/l2-readme.schema.json`
- **Create:** `templates/readme.j2`
- **Create:** `tools/cli/agency_ontology.py`
- **Modify:** `tools/fm/validate.py`

## Approach

1. **Gate 1 — Confidence:** The centralized ontology concept is fully researched. The schemas MUST strictly adhere to JSON Schema Draft 07. The Jinja2 templates MUST gracefully handle missing optional fields.
2. **Gate 2 — TDD:** Write tests for the `agency_ontology.py` CLI and `validate.py` linter before implementation. Ensure RED → GREEN → REFACTOR.
3. **Schema Definition:** Author the L1 schema and the ontology header. Ensure the type enum covers all domains.
4. **Tooling Implementation:** Implement the `validate.py` updates to parse frontmatter and apply the schemas. Implement the `agency_ontology.py` CLI to drive the Jinja2 readme generation.
5. **Gate 3 — Evidence:** Provide stdout of passing tests and successful linting runs.
6. **Gate 4 — Self-Review:** Verify that no out-of-scope files were modified and that the schema correctly validates a representative sample of artifacts.

## Acceptance (Gherkin)

```gherkin
# anchor: 122.1
Scenario: L1 schema validates a representative sample from each domain
  Given the centralized L1 schema is active
  When the linter evaluates a valid spec, track, and skill file
  Then the validation succeeds without errors

# anchor: 122.2
Scenario: Edge linter detects a broken edge
  Given an artifact defines a "spec_depends_on" edge
  And the target of that edge does not exist
  When the ontology linter runs
  Then it MUST fail with an error detailing the broken edge

# anchor: 122.3
Scenario: Auto-readme renderer is byte-identical on second run
  Given a valid artifact file
  When the readme generator runs
  And it runs a second time
  Then the output MUST be byte-identical

# anchor: 122.4
Scenario: A missing required L2 readme field fails CI
  Given a readme artifact (type = "readme") missing a required L2 field declared in `l2-readme.schema.json`
  When the linter evaluates the file
  Then it MUST fail validation with a specific L2 error citing the missing field name
  And the error MUST identify the L2 schema (`l2-readme.schema.json`) as the source of the rejection
  (Per-domain L2 schemas — `l2-music-track.schema.json`, `l2-novel-work.schema.json`, etc. — are out of scope for this spec; they ship in their respective domain specs and reuse this validator.)

# anchor: 122.5
Scenario: Context Mode Path B `context_search` returns ontology-typed results
  Given the context manifest is built with the new ontology
  When context_search is queried
  Then the returned entries MUST include the correct ontology "type" tag

# anchor: 122.6
Scenario: SUBDOC fenced div extracted by markdown-it-py
  Given a markdown file with a `::: {.gherkin id="122.6"}` fenced div
  When the linter parses the file
  Then the inner YAML+content MUST be exposed as a child ontology entry
  And the parent artifact MUST receive a `subdoc_contains: [122.6]` edge
```

## Findings highlights

(From `Plan/_research/centralized-ontology/findings.md` — full details there.)

**Type system (18 types — extended from PR #129's 12):**

| Domain | Types |
|---|---|
| Cross-cutting | `task`, `prompt`, `research`, `spec`, `readme`, `note`, `adr`, `gherkin` |
| Music | `track`, `album` |
| Novel | `work`, `chapter`, `ontology-entry` |
| Jules / agentic | `lesson` |
| Shared | `skill`, `override`, `reference`, `prompt-builder` |

(`spec` and `research` reused across jules/agentic — type is namespace-by-tag, not duplicated in the enum.)

**Placement modes retained from PR #129:**
- **STANDALONE** — entire file with frontmatter at top (~95% of artefacts)
- **SUBFILE** — parented by directory (e.g. `scenarios/01-happy-path.gherkin.md`)
- **SUBDOC** — Pandoc fenced div embedded in parent (`::: {.type id="x.y"} ... :::`). Restricted to `gherkin`, `note`, `ontology-entry`.

**Edge model (`header-ontology.json`):** typed edges with cardinality (one/many), declared forward-only (reciprocals auto-computed by the linter), e.g. `spec_depends_on(spec→spec, many)`, `track_belongs_to_album(track→album, one)`, `work_contains_chapter(work→chapter, many)`.

**Templating decision:** Jinja2 + Cog with a base `readme.j2` plus domain overrides (`skill_readme.j2`, `spec_readme.j2`, etc.). Data context includes parsed frontmatter + incoming/outgoing edges resolved from the manifest.

## Context Mode Path B integration

| Context Mode Path B surface | Integration point |
|---|---|
| **Spec 111 manifest** | `context_indexer.py` reads L1 frontmatter via `validate.py`. Tag taxonomy formalised: `domain:*`, `kind:*`, `topic:*`. Artefacts failing schema validation are EXCLUDED from the manifest (linter exit ≠ 0). |
| **Spec 112 describe** | `context_describe(id)` returns the L1 fields plus the `neighbours` object computed from `header-ontology.json` edges. Resolved edge targets are looked up against the same manifest. |
| **Spec 113 watcher** | When a file change event fires, the linter re-runs on the changed file. If schema violation, `status` is auto-flagged `blocked` in the manifest entry; watcher emits a separate `OntologyViolation` event. |

## Open questions

(See `Plan/_research/_synthesis-122-123-124.md` §4 for cross-spec rationale.)

| # | Question | Resolution (this spec) |
|---|---|---|
| **Q1** | SUBDOC parser choice | **PINNED**: `markdown-it-py`. Already a transitive dep, walks AST cleanly, handles nested div blocks. |
| **Q2** | Edge cleanup policy when target slug deleted | **FAIL-LOUD**. Linter exits non-zero with a `BROKEN_EDGE` diagnostic. No silent prune. |
| **Q3** | PR #129 ratification — does upstream `netzkontrast/agency` carry the 12-type ontology yet? | **TREAT AS DRAFT**. 122 extends to 18 types but stays a strict superset of PR #129's 12-type schema, so a future upstream merge is non-breaking. |
| Q6 | Schema migration for breaking ontology changes | Deferred. Migration CLI is a follow-up spec; for now `agency-ontology migrate --from <ver> --to <ver>` is out of scope. |
| Q7 | Full L2 treatment for `overrides/*.md` | **NO**. Overrides stay schema-less — they're cross-project user preferences, not catalogued artefacts. |

## Out of scope

- Full migration of all existing files to the new schemas. This spec only builds the foundation and tooling. The migration will occur incrementally in subsequent specs.
- Modifying the FastMCP server internals. The Context Mode handlers will consume the generated manifest, but the server code itself is not modified here.
- Schema migration for breaking ontology changes (Q6) — separate follow-up spec.
- L2 treatment for `overrides/*.md` (Q7) — overrides remain schema-less.

## References

- `Plan/JULES_PROTOCOL.md`
- `Plan/111-context-mode-manifest/spec.md`
- `Plan/_research/centralized-ontology/findings.md`
- `Plan/_research-briefs/01-centralized-ontology.md`
- `Plan/_research/_synthesis-122-123-124.md`
- `netzkontrast/agency` PR #129 (12-type ontology + 3-mode placement)
