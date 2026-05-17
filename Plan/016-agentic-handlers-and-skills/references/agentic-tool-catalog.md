# Agentic Orchestration Tool Catalog — embedded brief

> Embedded into `Plan/016-agentic-handlers-and-skills/` from upstream research note
> `look-at-the-code-inherited-toast-agent-acee154f8dd7033bf.md` (agentic-orchestration brief).
> Authoritative for Spec 016. Do not edit in place — bump the upstream and re-embed.

---

## 1. Tool catalog for `agency_mcp.handlers.agentic.*`

Design rule: **skills are the UI; tools are decidable / stateful primitives**. Each
tool either (a) runs a deterministic check no LLM is needed for, (b) renders a
fixed template from typed inputs, or (c) mutates persistent state with a schema.
Anything requiring judgement stays in the skill body.

### 1.1 `specs.py` — spec authoring / validation / audit (6 tools)

| Tool | Signature | Purpose | Kind |
|---|---|---|---|
| `spec_validate(path: str) -> ValidationReport` | in: spec path; out: `{ok, errors:[{rule, locator, msg}], warnings}` | BCP-14 keyword discipline (uppercase MUST/SHOULD/MAY, one-claim-per-statement), Gherkin parse, anchor↔statement cross-reference, §0–§9 schema slots present. | Decidable |
| `spec_audit(path: str, depth: "schema"\|"full") -> FindingsReport` | structured findings per `spec-skill` Mode-3 shape | Full audit including cross-cutting contradiction scan (statement ID graph). | Decidable (no LLM) |
| `spec_extract_statements(path: str) -> list[Statement]` | `[{id:"A.4.2", keyword:"MUST", actor, action, anchor_refs}]` | Parses normative statements into a typed list for downstream tools. | Decidable |
| `spec_extract_scenarios(path: str) -> list[GherkinScenario]` | `{anchor, feature, scenario, given, when, then}` | Gherkin-only extraction; feeds eval-set generation. | Decidable |
| `spec_derive_artifact(spec_path, target, out_dir)` | targets: `claude.md` \| `prompt` \| `checklist` \| `evalset` | Renders the chosen derivative with `# from X.Y.Z` provenance comments (Mode-2). | Mostly decidable |
| `spec_contradiction_scan(paths: list[str])` | cross-spec polarity/keyword conflict scan | Reuses `tools/check-rfc2119-polarity.py` logic. | Decidable |

### 1.2 `plans.py` — plan tracking, next-task, checkpointing (7 tools)

| Tool | Signature | Purpose | Kind |
|---|---|---|---|
| `plan_init(spec_path, plan_id, out_path) -> Plan` | Seeds a plan from a spec (one row per acceptance scenario / MUST). | Deterministic |
| `plan_get_next_task(plan_path, filter=None) -> Task\|None` | Returns next un-blocked, un-done task; honours `depends_on` + `priority`. | Decidable |
| `plan_mark_complete(plan_path, task_id, evidence)` | Stateful mutation with audit row. | Stateful |
| `plan_mark_blocked(plan_path, task_id, reason)` | Same. | Stateful |
| `plan_status(plan_path)` | Read-only roll-up. | Decidable |
| `plan_checkpoint(plan_path, label)` | Writes a git-trackable JSON snapshot under `checkpoints/`. | Stateful |
| `plan_diff(plan_path, snapshot_label)` | Compares current state to a checkpoint. | Decidable |

### 1.3 `workflows.py` — decomposition and status (5 tools)

| Tool | Signature | Purpose | Kind |
|---|---|---|---|
| `workflow_decompose(prd_path, strategy, depth)` | strategies: `systematic`\|`agile`\|`enterprise`; depths: `shallow`\|`normal`\|`deep` | Reads a PRD, returns phases + tasks + dependency edges. LLM-assisted; output schema decidable. | LLM-needed |
| `workflow_status(workflow_id)` | Stateful read. | Decidable |
| `workflow_advance(workflow_id, phase_id, evidence)` | Promote a phase `in_progress`→`done` after evidence supplied. | Stateful |
| `workflow_render_graph(workflow_id, format)` | Renders dependency DAG as Mermaid or Graphviz DOT. | Decidable |
| `workflow_register_evidence(workflow_id, task_id, artefact_path)` | Append-only evidence log. | Stateful |

### 1.4 `research.py` — research-brief rendering + intent capture (5 tools)

| Tool | Signature | Purpose | Kind |
|---|---|---|---|
| `research_intent_capture(seed_query, out_path)` | Phase-1 of `research-prompt-optimizer` → intent YAML. | LLM-needed |
| `research_brief_render(intent_yaml, out_dir, modules=None)` | Deterministic Python render mirroring `render/render.py`. | Decidable |
| `research_brief_audit(brief_path)` | Reader-test simulation: fresh reader can locate task, constraints, deliverable, success criteria. | LLM-needed |
| `research_brief_finalize(brief_path, out_zip)` | Packages artefact set per Phase-5 finalize. | Decidable |
| `research_catalog_list(category=None)` | Returns catalog (A/B/C × M01–M12 etc.) for module selection. | Decidable |

### 1.5 `ralph.py` — Ralph file rendering (5 tools)

| Tool | Signature | Purpose | Kind |
|---|---|---|---|
| `ralph_render(spec_path, out_dir, variant, enhancements)` | variants: `base`\|`enhanced`\|`streamed`\|`git-worktrees` | Emits `loop.sh`, `PROMPT_build.md`, `PROMPT_plan.md`, `AGENTS.md`, `IMPLEMENTATION_PLAN.md`. | Decidable |
| `ralph_extend(ralph_dir, extensions)` | Adds specs-mode / plan-work / SLC / reverse-engineer files + patches `loop.sh`. | Decidable |
| `ralph_audit(ralph_dir)` | Mode-4 checks: placeholders, backpressure commands real, AGENTS.md length, model strings current. | Decidable |
| `ralph_customize(ralph_dir, fields)` | Fills placeholders without regenerating. | Decidable |
| `ralph_research_bridge(research_doc, ralph_dir)` | Four-part JTBD framing per ralph-skill Research Bridge. | LLM-assisted |

### 1.6 `confidence.py` — pre-implementation gating (4 tools)

| Tool | Signature | Purpose | Kind |
|---|---|---|---|
| `confidence_check(task_brief, repo_root)` | `{total: 0.0–1.0, breakdown:{...}, recommendation: "go"\|"clarify"\|"stop"}` | Five-check rubric of `sc-confidence-check`. | Mixed |
| `confidence_duplicate_scan(query, repo_root)` | Grep/Glob duplicate search. | Decidable |
| `confidence_doc_verify(api_or_pkg, version)` | WebFetch official docs; cache. | LLM-light |
| `confidence_oss_reference(pattern)` | WebSearch for working OSS references. | LLM-light |

**Module-count total: 32 tools across 6 modules.** Each module ships a typed
Pydantic schema + a `_state.py` for SQLite cache access.

## 2. State persistence — markdown + SQLite hybrid

Layout under `~/.agency-system/agentic/`:

```
plans/<spec-slug>/{plan.md, tasks/T<NNN>-*.md, checkpoints/<iso>.json}
workflows/<workflow-id>/{workflow.md, phases/<NN>-<slug>.md, evidence/<task_id>/*}
specs/<slug>/{spec.md, audit.json, derived/}
research/<slug>/{intent.yaml, brief.md, render.log}
ralph/<project>/{loop.sh, PROMPT_*.md, AGENTS.md, IMPLEMENTATION_PLAN.md}
cache/index.db          # SQLite — derived; safely rebuildable from markdown
locks/*.lock            # file-lock per artefact
```

Rules:

1. Markdown + frontmatter is the only source of truth.
2. `cache/index.db` is rebuildable. Schema: `artefacts(path, type, status, slug, updated_at, hash)`, `plan_tasks(plan_id, task_id, status, depends_on, evidence_path)`, `audit_findings(spec_path, rule, locator, severity, msg)`.
3. JSON checkpoints are point-in-time snapshots — not authoritative.
4. No in-memory state beyond a single tool call.
5. File locks mirror `tools/fm/edit.py` semantics.
6. Per-spec `audit.json` cache invalidated by `updated:` frontmatter bump.

## 3. Code Mode & orchestration conventions

### 3.1 `dry_run` convention (RECOMMENDED for every stateful tool)

Every tool in `plans.py`, `workflows.py`, `ralph.py` (write paths), and
`research.py` (render/finalize) **MUST** accept `dry_run: bool = False`. When
`dry_run=True`:

- No filesystem writes, no SQLite mutations, no lock acquisition.
- Return value is `{would_apply: <full payload>, diff: <markdown diff vs current>, warnings: [...]}`.
- Idempotent and safe to re-call.

Decidable tools (`spec_validate`, `plan_status`, `workflow_render_graph`,
`confidence_check`) do not need `dry_run` — they are already read-only.

### 3.2 Plan-return convention (`return_plan`)

Orchestration tools (`workflow_decompose`, `ralph_render`, `research_brief_render`,
`spec_derive_artifact`) accept `return_plan: bool = False`. When `True`:

- Return `OrchestrationPlan = {steps: [{tool, args, expected_artefacts: [path]}], cost_estimate: tokens, side_effects: [...]}`.
- Agent inspects, decides, then re-calls with `commit=True`.

### 3.3 Shared `ToolResult` envelope (every tool)

```python
class ToolResult(BaseModel):
    ok: bool
    data: Any                          # the typed payload
    warnings: list[str] = []
    artefacts_written: list[str] = []  # absolute paths; empty in dry_run
    next_suggested_tools: list[str] = []
```

### 3.4 Error semantics

- Validation failures → `ok=False`, `data=ValidationReport`, exit cleanly (do not raise).
- I/O failures (lock contention, disk) → raise; the harness retries.
- LLM-needed tools that get no model → `ok=False`, `data=None`, `warnings=["model_unavailable"]`.

## 4. Provenance

- Upstream: `/root/.claude/plans/look-at-the-code-inherited-toast-agent-acee154f8dd7033bf.md`
- Reproduced verbatim except for table-column re-flowing for spec-folder render width.
- Citations preserved in the upstream note: GitHub Spec Kit, Martin Fowler SDD survey,
  Cloudflare Code-Mode post, Anthropic "Code execution with MCP", FastMCP Code-Mode
  transform docs, memweave / sqliteai-sqlite-memory / palinode (markdown+SQLite pattern).
