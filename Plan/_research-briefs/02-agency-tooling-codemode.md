---
type: research-brief
status: dispatched
slug: agency-tooling-codemode
summary: "Jules research brief — extract netzkontrast/agency's frontmatter/ontology tooling (~30 check-*.py + lint-*.py scripts, tools/fm/, maintenance/schemas/) and design a Plan spec that integrates them as FastMCP Code Mode tools + PostToolUse hooks for the-agency-system plugin. Output: findings doc + draft Plan Spec 123."
dispatched_to: jules
dispatched_at: 2026-05-18
parent_specs: [008, 111, 112, 113]
sibling_brief: 01-centralized-ontology.md
output_branch: research/agency-tooling-codemode
output_files:
  - Plan/_research/agency-tooling-codemode/findings.md
  - Plan/_research/agency-tooling-codemode/draft-spec.md
---

# Research Brief — Agency Tooling Extraction + MCP Code Mode Integration

This is the prompt body dispatched to Jules via `jules-bulk fanout`. Sibling brief: `01-centralized-ontology.md` (this brief assumes its data-shape outputs as inputs but does not block on them).

---

## 1. Goal (one sentence)

Produce a research findings document + a draft Plan spec (`spec_id: 123`, `slug: agency-tooling-codemode`) that **catalogues the validation/lint/render/audit tooling in `netzkontrast/agency`'s `tools/`, `maintenance/schemas/`, and proposed `agency` CLI**, then designs how each becomes a **FastMCP tool registered via the Code Mode registry (Spec 008)** and/or a **PostToolUse hook** in `the-agency-system` plugin — so the centralized ontology from Brief 1 has machinery to enforce it.

## 2. Why this matters

Brief 1 produces the *data shape* (types, schemas, edges, modes, ULIDs). It does **not** produce the machinery to validate, render, or query the ontology. That machinery already exists in agency in mature form — ~30 single-purpose Python checkers, a frontmatter loader, a schema-mirror generator, a governance gate, a linkage linter, and the *proposed* `agency` CLI in PR #129's `migration/adr-draft.md`. Porting these into FastMCP tool form makes them callable from skills, from hooks, and (via the Code Mode triad) from the model itself.

Three concrete wins:

1. **Skills become enforcement points.** A music skill can call `ontology_validate_frontmatter(path)` before committing a track edit; a novel skill can call `ontology_check_audit_graph()` before opening a PR; the agentic side can call `ontology_render_readme(path)` to refresh an auto-readme.
2. **PostToolUse hooks become deterministic.** The plugin already runs `hooks/validate_track.py` and `hooks/validate_chapter.py` (per `Plan/000-overview.md` §1 and §2.1 #11). Centralized ontology hooks replace per-domain validators with a single `hooks/validate_ontology.py` that consults the L1/L2 schemas.
3. **Code Mode gets ontology-aware anchors.** Spec 112's `context_search` returns BM25 hits; an `ontology_query(type, edge, target)` anchor returns graph-walked hits — the model can ask "give me every spec whose `depends_on` includes 008" in one call instead of grepping.

## 3. Required reading

1. **netzkontrast/agency `main` — tools/ inventory.** For each file under `tools/` (excluding `tools/legacy/` and `tools/tests/`), record: name, ~LOC, public CLI signature, what it validates/lints/renders, what it depends on (other tools, schemas, ontology files).
   - Validators (one per file): `validate-frontmatter.py`, `check-assumption-log.py`, `check-audit-graph-consistency.py`, `check-canon-status.py`, `check-clean-working-directory.py`, `check-external-result-downstream-task.py`, `check-fl-declaration.py`, `check-governance.sh`, `check-hard-rules.py`, `check-hooks.py`, `check-maintenance-bypass.py`, `check-narrative-ontology-load.py`, `check-prompt-framework-declaration.py`, `check-prompt-self-containedness.py`, `check-readme-frontmatter.py`, `check-rfc2119-polarity.py`, `check-spec-runtime-state.py`, `check-trust-audit.py`, `check-trust.py`, `check-worksheet-order.py`, `check-workspace-cleanliness.py`
   - Linters: `lint-linkage.py`, `lint-runlog.py`, `lint-structure.py`
   - Helpers: `_frontmatter.py`, `tools/fm/*` (loader, validator, schema-mirror generator)
   - Sub-tools: `tools/adr/`, `tools/dramatica-nav/`
   - Hooks installer: `install-hooks.sh`
2. **netzkontrast/agency `main` — schemas inventory.**
   - `maintenance/schemas/l1-vault-core.schema.json`
   - Every `maintenance/schemas/l2-<type>.schema.json`
   - `maintenance/schemas/header-ontology.json`
3. **netzkontrast/agency PR #129** — proposed-but-unbuilt tooling:
   - `migration/adr-draft.md` — `agency` CLI surface (`agency readme`, `agency promote`, `agency new`, …)
   - `migration/schemas-delta.md` §6–§8 — new validator flags (`--check-mode`, `--check-readme`), new governance steps, new lint-structure paths
4. **the-agency-system Plan/** — integration surfaces:
   - `Plan/000-overview.md` §2.1 (FastMCP conventions — tool naming, snake_case, ≤120-char docstrings, tags, response shapes, `dry_run` for stateful tools, `return_plan` for orchestration, `ToolResult` envelope), §2.1 #10 (StateCache lifecycle), §2.1 #11 (hooks discipline — synchronous correctness in tool, hooks only for side effects)
   - `Plan/008-codemode-registry/spec.md` — Code Mode registry, `eager` / `deferred` / `background` classification, `defer_schema=True`
   - `Plan/111`–`Plan/113` — Path B specs (manifest + anchor-triad + cache/watcher)
   - `Plan/016-agentic-handlers-and-skills/spec.md` — agentic-domain tool catalogue (~32 tools) for naming consistency
   - `Plan/017-hooks-port-and-extend/spec.md` — hooks contract for `hooks/hooks.json`
5. **External references:**
   - FastMCP Code Mode docs: <https://gofastmcp.com/servers/transforms/code-mode>
   - FastMCP `@mcp.tool` / `tags=` / `defer_schema`: <https://gofastmcp.com/servers/tools>
   - Claude Code hooks (PreToolUse / PostToolUse / SessionStart / PreCompact / UserPromptSubmit): <https://docs.claude.com/en/docs/claude-code/hooks>
   - MCP 2025-06-18 server spec: <https://modelcontextprotocol.io/specification/2025-06-18>

## 4. Source clones

Reuse Brief 1's clone if present; otherwise:

```bash
git clone --depth=1 --branch=main \
  https://github.com/netzkontrast/agency.git \
  ~/work/vendor/agency
cd ~/work/vendor/agency && git fetch origin pull/129/head:pr-129
```

Read-only. Never commit anything from `~/work/vendor/`.

## 5. Output

Two files on a new branch `research/agency-tooling-codemode` rooted at `Master`:

### 5.1 `Plan/_research/agency-tooling-codemode/findings.md`

A research report (~600–1200 lines). Structure:

1. **Executive summary** (≤300 words) — total tool count, recommended port count, recommended Code Mode classification breakdown (eager / deferred / background).
2. **Inventory table** — one row per agency `tools/*.py`. Columns: `name`, `category` (validator/lint/render/audit/helper/CLI), `LOC`, `CLI signature`, `inputs`, `outputs`, `exit-code semantics`, `dependencies`, `would-it-port-cleanly?` (yes / yes-with-shim / no / out-of-scope).
3. **Mapping to FastMCP tools** — for every tool in the inventory marked "yes" or "yes-with-shim":
   - Proposed FastMCP tool name (snake_case `ontology_<verb>_<object>` per overview §2.1 #1)
   - One-line docstring (≤120 chars, imperative)
   - Tags (`tags={"domain:agentic", "kind:ontology", …}`)
   - Classification — `eager` (anchor) | `deferred` | `background` (with `*_status` poll companion)
   - Whether it's `dry_run`-capable (overview §2.1 #7)
   - Whether it's orchestrational (needs `return_plan: bool`, §2.1 #8)
   - Suggested handler module path under `servers/agency-mcp/src/agency_mcp/handlers/ontology/`
4. **Anchor triad design** — propose 3–5 *eager* anchor tools that cover 80 % of likely calls:
   - e.g. `ontology_validate_frontmatter(path)`, `ontology_check_graph_consistency()`, `ontology_render_readme(path, dry_run=True)`, `ontology_query(type, edge?, target?)`, `ontology_govern(scope="repo"|"path")`
   - Mirror Spec 104's `agency_tool_search` / `agency_tool_describe` / `agency_tool_invoke` triad pattern
   - Token-budget estimate per anchor (must stay within Spec 008's boot budget; cite the §2.1 #4 ~315-token target)
5. **PostToolUse / PreToolUse hook design** — which validators wire into `hooks/hooks.json` and on which events:
   - Music: `validate_track.py` → ontology equivalent
   - Novel: `validate_chapter.py` → ontology equivalent
   - Cross-domain: `validate_frontmatter` PostToolUse on every Write/Edit that touches a Markdown file with frontmatter
6. **Code Mode registry integration** (Spec 008) — how the new tools register: `register_ontology_handlers(mcp)` + `apply_codemode_manifest(mcp, …)` entries in `codemode/manifest.json` with `classification` and `anchor_kind`.
7. **The `agency-system-ontology` CLI surface** — analogue of agency's proposed `agency` CLI: which subcommands ship, what they do, whether each subcommand is *both* a CLI entry point *and* a FastMCP tool (the recommended pattern — single Python module, two entry points).
8. **Migration sequence** — port order. Recommended: helpers (`_frontmatter.py`, `fm/`) first; then L1 validator; then governance gate; then per-type L2 validators; then linkage/structure linters; then audit-graph; then render-readme; then `agency` CLI promotion semantics.
9. **What NOT to port** — call out tools that don't fit (e.g. agency-repo-specific governance like `check-canon-status.py` if its concept doesn't map to this plugin's content model).
10. **Risks & costs** — LOC estimate, Python version constraints, test surface, interaction with existing `hooks/validate_*.py`.
11. **References** — every cited URL, file path, commit SHA.

### 5.2 `Plan/_research/agency-tooling-codemode/draft-spec.md`

A draft Plan spec following the exact template of `Plan/111-context-mode-manifest/spec.md`. Apply the **`spec-skill` skill conventions** for normative authoring:

- **BCP-14 / RFC-2119 keywords** (MUST / MUST NOT / SHOULD / SHOULD NOT / MAY) in Done When + Approach.
- **Gherkin acceptance criteria** — minimum 6 scenarios covering: (a) frontmatter validation on a representative file from each domain, (b) graph-consistency check detects a broken edge, (c) readme auto-render is byte-identical on second run with no source change, (d) Code Mode boot token budget ≤ 5 % overhead per added anchor (per Spec 112's bar), (e) a PostToolUse hook fires within 500 ms on an Edit of a frontmatter-bearing file, (f) `dry_run=True` returns `{would_apply, diff, warnings}` without mutating anything (overview §2.1 #7).
- **Frontmatter**: `spec_id: 123`, `slug: agency-tooling-codemode`, `status: draft`, `owner: jules`, `depends_on: [008, 111, 122]` (122 = Brief 1's draft spec; cite as soft dependency since 122 is still draft), `affects: <list>`, `source-repos: [netzkontrast/agency @ main]`, `estimated_jules_sessions: 2`, `domain: cross`, `wave: D`.
- Standard sections: Why · Done When · Source clones · Files (Create / Modify / Delete) · Approach (Gates 1–4) · Acceptance · Out of scope · References.

## 6. Acceptance — when is this brief "done"?

- [ ] `Plan/_research/agency-tooling-codemode/findings.md` exists, ≥ 600 lines, inventory table has one row per agency tool examined.
- [ ] `Plan/_research/agency-tooling-codemode/draft-spec.md` exists, follows the Spec 111 template, passes `spec-skill` BCP-14 audit.
- [ ] PR opened from `research/agency-tooling-codemode` → `Master` with Gates 1–4 in the body.
- [ ] No code under `servers/agency-mcp/` is modified. Research-only.
- [ ] Vendor source under `~/work/vendor/agency/` is not committed.

## 7. Anti-patterns (Jules MUST NOT)

- Verbatim-paste the Python source of agency's checker scripts into findings.md — summarise behaviour, link by path + commit SHA.
- Propose new ontology types (that's Brief 1's territory) — assume Brief 1's draft Spec 122 will produce the type set; reference it as `[spec:122]` even though it doesn't exist yet.
- Try to design the music/novel-side hook ports in detail — that's Spec 017's territory. This brief proposes the *cross-cutting* `validate_ontology.py` only.
- Skip the `dry_run` / `return_plan` / `ToolResult` envelope discipline from overview §2.1 — every proposed tool must declare its compliance.
- Bypass the FastMCP `tags=` requirement (`domain:*`, `kind:*`, `anchor_kind:*`).

## 8. Estimated effort

2 Jules sessions, ~6–8 hours wall-clock total. The inventory pass is mechanical; the Code Mode integration design is the load-bearing analytical step.
