---
spec_id: 123
slug: agency-tooling-codemode
status: ready
owner: jules
depends_on: [008, 111, 122]
affects:
  - servers/agency-mcp/src/agency_mcp/handlers/ontology/
  - servers/agency-mcp/src/agency_mcp/handlers/ontology/__init__.py
  - servers/agency-mcp/src/agency_mcp/codemode/manifest.json
  - hooks/hooks.json
  - hooks/validate_ontology.py
domain: cross
wave: D
estimated_jules_sessions: 2
source-repos: [netzkontrast/agency @ main]
research: Plan/_research/agency-tooling-codemode/findings.md
---

# Spec 123: Agency Tooling Extraction + MCP Code Mode Integration

## Why

Spec 122 establishes a centralized ontology data shape (types, schemas, edges, modes). However, a data shape is inert without machinery to enforce it. The `netzkontrast/agency` repository contains a mature suite of Python validation, linting, rendering, and auditing tools (`tools/fm/`, `check-*.py`).

By extracting these tools and wrapping them as FastMCP Code Mode tools (Spec 008) and `PostToolUse` hooks within `the-agency-system`, we give the model native, programmatic access to the ontology. Skills can validate pre-commit invariants, hooks become deterministic via unified schemas, and graph-aware queries can resolve complex context dependencies efficiently.

## Done When

- The agency `fm` tooling and relevant `check-*.py` scripts MUST be ported to `agency_mcp/handlers/ontology/`.
- Four eager anchor tools (`ontology_validate_frontmatter`, `ontology_check_graph_consistency`, `ontology_render_readme`, `ontology_query`) MUST be registered and documented. Combined token budget ≤ 170 tokens absolute. (The "5 % of baseline" framing from earlier drafts was incorrect: Spec 008's Code-Mode baseline is ~315 tokens per overview §2.1 rule 4, so 170 is ~54 % of that absolute number. The operative budget gate for Wave D is the *cumulative* `tools/list` size staying within 1.10× of the pre-Wave-D baseline — see synthesis §4 Q4 and acceptance 123.4 — verified by `bin/measure_token_budget` after each spec lands.)
- The `servers/agency-mcp/src/agency_mcp/codemode/manifest.json` MUST classify each tool as `eager`, `deferred`, or `background` per the table in §Findings highlights below.
- A centralized `hooks/validate_ontology.py` MUST be registered in `hooks/hooks.json` to fire PostToolUse on edits to Markdown files with frontmatter; total wall-time MUST stay ≤ 500 ms.
- Tool responses MUST adhere to the token-efficiency policy, returning summaries by default (`view=summary`, see Spec 103).
- Stateful tools MUST support `dry_run=True` and return the `{would_apply, diff, warnings}` envelope.
- 6 explicitly out-of-scope agency tools (see §Out of scope) MUST NOT be ported.

## Source clones

```bash
git clone --depth=1 --branch=main https://github.com/netzkontrast/agency.git ~/work/vendor/agency
cd ~/work/vendor/agency && git fetch origin pull/129/head:pr-129
```

## Files

**Create:**
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/__init__.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/validate.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/graph.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/render.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/query.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/edit.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/govern.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/rename.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/fix.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/_core.py`
- `hooks/validate_ontology.py`

**Modify:**
- `servers/agency-mcp/src/agency_mcp/codemode/manifest.json`
- `hooks/hooks.json`

## Approach

### Gate 1 — Confidence & Design

The `netzkontrast/agency` tools are standalone Python files that rely heavily on `argparse` for inputs. We will extract the CLI argument parsing and replace it with strongly typed Pydantic models conforming to the FastMCP `@mcp.tool()` signature requirement. Tool docstrings MUST be strictly ≤ 120 characters and imperative to comply with overview §2.1. Tool names MUST follow the snake_case `ontology_<verb>_<object>` convention.

### Gate 2 — TDD / Red-Green-Refactor

Write pytest cases against `servers/agency-mcp/src/agency_mcp/handlers/ontology/` verifying the core behavior independent of the MCP server:

1. Valid frontmatter correctly parses and passes.
2. Invalid frontmatter fails and produces structured `Diagnostic` outputs.
3. Graph cyclic dependencies are accurately detected.
4. `dry_run=True` mutates zero bytes on disk and correctly computes diffs.

### Gate 3 — Evidence

Provide pytest stdout output and MCP local tool invocation payloads proving the anchor tools return correct shapes under the required token budget. Provide logs of the `PostToolUse` hook successfully catching an edit.

### Gate 4 — Self-Review

Verify `return_plan` usage, ensure the correct tag namespaces are utilized (`domain:agentic`, `kind:ontology`, `anchor_kind:eager`), and confirm hook timing constraints are satisfied. Document explicitly if any structural logic deviates from PR #129.

## Acceptance (Gherkin)

```gherkin
# anchor: 123.1
Scenario: Frontmatter validation on a representative file
  Given a `task.md` with missing required frontmatter fields
  When `ontology_validate_frontmatter("task.md")` is called
  Then the tool MUST return an ERROR diagnostic citing the schema violation

# anchor: 123.2
Scenario: Graph-consistency check fails loud on a broken edge
  Given a spec artifact with a `depends_on` edge pointing to a non-existent slug
  When `ontology_check_graph_consistency()` is called
  Then the tool MUST emit a `BROKEN_EDGE` ERROR diagnostic
  And the CLI MUST exit non-zero (per Spec 122 Q2 fail-loud policy)

# anchor: 123.3
Scenario: Readme auto-render is byte-identical
  Given a complete set of frontmatter inputs
  When `ontology_render_readme(path)` is run twice consecutively
  Then the second run MUST yield a byte-identical markdown output to the first

# anchor: 123.4
Scenario: Code Mode boot token budget
  When the `ontology` namespace is booted
  Then the 4 eager anchor tools MUST contribute ≤ 170 total tokens
  And the total combined manifest impact MUST remain ≤ 1.10× Spec 008 baseline

# anchor: 123.5
Scenario: PostToolUse hook timing
  When a `Write` tool modifies a Markdown file containing frontmatter
  Then the `PostToolUse` hook running `validate_ontology.py` MUST fire
  And the hook MUST complete within 500 ms

# anchor: 123.6
Scenario: `dry_run=True` behavior
  Given a valid `ontology_edit_frontmatter` command with `dry_run=True`
  When the tool is invoked
  Then it MUST return a `{would_apply, diff, warnings}` dictionary
  And the underlying file MUST NOT be mutated
```

## Findings highlights

(From `Plan/_research/agency-tooling-codemode/findings.md` — 601 lines, full inventory there.)

**Tool catalogue (46 tools inventoried):**

| Bucket | Count | Examples |
|---|---|---|
| Validators (`check-*.py`) | 19 | frontmatter, audit-graph, hard-rules, RFC-polarity, trust-audit, worksheet-order |
| FM core (`fm/`) | 14 | edit, extract, fix, graph, validate, rename, query, skills_query, new, section, index_diff, gen_schema_mirror |
| Linters (`lint-*.py`) | 3 | linkage, runlog, structure |
| CLI orchestrators | 2 | `check-governance.sh`, `fm.py` |
| Helpers | 3 | `_frontmatter.py`, `_core.py` (973 LOC), `_lifecycle_signals.py` |
| Install / shell wrappers | 5 | install-hooks.sh, install-superclaude.sh, etc. (out-of-scope) |

**Eager / deferred / background classification (Spec 008 tiers):**

| Tool | Tier | Token est. | Rationale |
|---|---|---|---|
| `ontology_validate_frontmatter` | eager | ~45 | Path-only input, instant feedback. |
| `ontology_check_graph_consistency` | eager | ~20 | Macro-level audit, terminal validation. |
| `ontology_render_readme` | eager | ~45 | Standard task closure; `dry_run=True` built-in. |
| `ontology_query` | eager | ~60 | Graph navigation; enables context retrieval. |
| **Subtotal eager** | — | **~170** | Under the 315-token Spec 112 anchor ceiling. |
| `ontology_govern` | background | — | Runs 6 lint passes async; companion `ontology_govern_status(job_id)`. |
| `ontology_edit_frontmatter` | deferred | — | Stateful multi-key edit. |
| `ontology_rename_slug` | deferred | — | Sweeping multi-file side-effects → `return_plan` envelope. |
| `ontology_fix_auto_repairs` | deferred | — | Auto-repair recipe engine → `dry_run` required. |

**PostToolUse hook (`hooks/validate_ontology.py`):**
1. MCP fires hook after successful `Write` or `Edit` on `*.md` files containing `---` frontmatter (Claude Code exposes both tools — the matcher in `hooks/hooks.json` MUST be `"Edit|Write"` so frontmatter-touching edits via `Edit` are not bypassed). **Bash-written files** (e.g. `echo ... > file.md`, `cat << EOF > file.md`) do NOT trigger PostToolUse for `Edit|Write` — those are caught by the FS-level safety net at Spec 113's watcher, which dispatches `validate_ontology.py` on every `ChangeEvent` regardless of the tool that produced the change. The hook is the fast path for in-Claude-Code edits; the watcher is the source-agnostic backstop.
2. Hook invokes `ontology_validate_frontmatter(path)` synchronously.
3. Diagnostics returned to agent context.
4. Hook is **read-only** — never mutates files; graph traversal deferred to `ontology_govern`.
5. 500 ms budget achieved by eager-loading schemas at module init + `jsonschema` caching.

## Path B integration

| Path B surface | Integration point |
|---|---|
| **Spec 111 manifest** | The manifest builder calls `ontology_validate_frontmatter` per file; violations downgrade `status` and exclude the entry from search results. |
| **Spec 112 describe** | `context_describe(id)` enriches its payload with `ontology_query(id, expand=neighbours)` to add the resolved edge graph. |
| **Spec 113 watcher** | On `ChangeEvent`, the watcher dispatches `hooks/validate_ontology.py` first, then re-runs the manifest indexer if validation succeeds. |
| **Spec 122 schemas** | This spec **implements the validators that 122 declares**. Spec 122 owns the schema artefacts; Spec 123 owns the runtime enforcement. |

## Open questions

(See `Plan/_research/_synthesis-122-123-124.md` §4 for cross-spec rationale.)

| # | Question | Resolution (this spec) |
|---|---|---|
| **Q3** | PR #129 ratification | **Unratified upstream as of 2026-05-18 (user decision).** Validators in this spec enforce Spec 122's strict 18-type superset. The 12-type subset remains a future-merge-compatible subset (non-breaking). Tool MUST hot-reload schema files on first call after edit. |
| **Q4** | Combined boot-token budget | ≤ 170 tokens for eager-anchor 4; re-measure via `bin/measure_token_budget` after merge. |
| TBD | `ontology_edit_frontmatter` return envelopes | Wrapped in the shared `ToolResult` shape (overview §2.1 #9). Happy path: `{ok: True, data: {new_frontmatter: {...}, lines_changed: int}, warnings: [...], artefacts_written: [path], next_suggested_tools: [...]}`. Dry-run (`dry_run=True`) per §2.1 #7: `{would_apply, diff, warnings}` — never mutates disk. Findings did not specify; this spec pins both. |
| TBD | Graph cache invalidation API | After any `ontology_edit_*` or `ontology_rename_*`, call `graph.invalidate_node(id)`; if Spec 124 is live, also triggers `graph_ingest_frontmatter`. |
| TBD | Concurrency under asyncio | All stateful tools acquire a per-namespace `asyncio.Lock`; reads are lock-free against the in-memory schema cache. |
| TBD | Diagnostic JSON schema | Pin: `{code: str (UPPER_SNAKE), severity: "error"|"warning"|"info", path: str, line: int|null, message: str, hint: str|null}`. Error codes enumerated in `_core.py`. |

## Out of scope

These 6 agency tools are explicitly **NOT** ported (per findings §1 — they don't generalise across plugin domains):

- `check-canon-status.py` — Git branch fast-forward tracking, workflow-specific to netzkontrast/agency.
- `check-hard-rules.py` — subjective writing style.
- `check-rfc2119-polarity.py` — NLP model inference (token-heavy, eager-anchor incompatible).
- `check-external-result-downstream-task.py` — netzkontrast workflow task chaining.
- `check-trust.py` + `check-trust-audit.py` — explicit trust-level / cryptographic audit.

Also out of scope:

- Domain-specific validators (`validate_track.py`, `validate_chapter.py`) — superseded by the single generalised `validate_ontology.py` hook.
- Designing music/novel domain validators (Spec 017 territory).
- Schema migration for breaking ontology changes (Q6 from synthesis — deferred to a follow-up spec).

## References

- `Plan/008-codemode-registry/spec.md`
- `Plan/111-context-mode-manifest/spec.md`
- `Plan/122-centralized-ontology/spec.md`
- `Plan/_research/agency-tooling-codemode/findings.md`
- `Plan/_research-briefs/02-agency-tooling-codemode.md`
- `Plan/_research/_synthesis-122-123-124.md`
- netzkontrast/agency `tools/fm/` + `check-*.py`
