---
spec_id: 136
slug: agents-yaml-role-manifest
status: draft
owner: jules
depends_on: [099]
affects:
  - agents.yaml
  - Plan/_lint/check_agents_yaml.py
  - Plan/_lint/check_agent_handoff.py
  - servers/agency-mcp/src/agency_mcp/handlers/agentic/agents_registry.py
  - servers/agency-mcp/src/agency_mcp/handlers/agentic/__init__.py
  - tests/unit/agentic/test_agents_registry.py
  - tests/unit/agentic/test_agent_handoff.py
  - tests/unit/agentic/fixtures/agents-valid.yaml
  - tests/unit/agentic/fixtures/agents-broken-quota.yaml
  - tests/unit/agentic/fixtures/agents-broken-cycle.yaml
  - docs/architecture/agent-role-manifest.md
  - Plan/JULES_PROTOCOL.md
source-repos: []
estimated_jules_sessions: 2
domain: agentic
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 136 — `agents.yaml` Role Manifest + Hand-off Registry

## Why

`Plan/JULES_PROTOCOL.md` describes how *Jules* should behave but the repository already coordinates **four** distinct agent classes: **Jules** (async cloud worker, fan-out, ≤5 daily slots), **Codex** (PR-bot reviewer, asynchronous comment author), **Cursor / Continue** (interactive IDE-side MCP clients addressed by Spec 023), and **local Claude subagents** (in-session `Agent` tool dispatched per `superpowers-dispatching-parallel-agents`). The orchestrator (Claude Opus driving the session) routes work between them without a machine-readable contract — Codex's review-vs-merge precedence, Jules's quota, Cursor's MCP-pass-through, and local-subagent role boundaries all live in prose. Result: every new spec re-discovers the same hand-off rules and the `affects:` checker (Spec 099) cannot mechanically verify "this spec dispatches the right agent class". Spec 023 (harness-in-harness) opens the surface to *external clients* but does not formalize *agent identity* — who is calling, with what quota, with what hand-off pre/post-conditions. Spec 099 patches `JULES_PROTOCOL.md` but does not generalize beyond Jules.

This spec ships `agents.yaml` (single repo-root YAML manifest), three MCP discovery tools, two lint scripts, and a Gherkin-checked hand-off contract — so every future spec can declare `agent_class: jules` or `agent_class: codex-review` and the toolchain mechanically validates routing, capability fit, quota envelopes, and the hand-off pair (e.g. `jules → codex-review → human-merge`).

## Done When

- [ ] `agents.yaml` exists at repo root, parses as YAML, and validates against `state/schema/agents.schema.json` (created by this spec). It enumerates ≥4 agent classes with: `class`, `display_name`, `runtime` (one of `cloud-async`, `cloud-bot`, `ide-mcp-client`, `local-subagent`, `local-orchestrator`), `capabilities[]`, `quota` (`daily_slots`, `concurrent`, `tokens_per_session`), `pr_authorship` (`true` | `false` | `bot-co-author`), `closing_run_path` (`/sc:createPR` | `jules-finalize` | `n/a-comment-only` | `local-commit`), `escalation_target` (another class slug or `human`), and `handoff_triggers[]` (each entry: `from_status`, `to_class`, `payload_shape`).
- [ ] `Plan/_lint/check_agents_yaml.py` exists, validates schema conformance, AND emits one diagnostic per anomaly. Diagnostic codes: `AGENTS.SCHEMA` (schema violation), `AGENTS.UNKNOWN_CLASS` (`escalation_target` references undefined class), `AGENTS.QUOTA_INVALID` (negative or zero `concurrent`), `AGENTS.HANDOFF_CYCLE` (cycle in `handoff_triggers` graph).
- [ ] `Plan/_lint/check_agent_handoff.py` exists and walks every `Plan/*/spec.md`. When a spec's frontmatter declares `owner: <class>`, the lint script verifies the class exists in `agents.yaml` AND the spec's Approach section names the expected hand-off pair from `agents.yaml.handoff_triggers`. Diagnostic code `AGENTS.HANDOFF_MISSING` fires when an `owner: jules` spec does not mention either `codex` review or `local-subagent` review per the registry.
- [ ] Three MCP tools added under `domain:agentic`:
  - `agents_list()` → `[{class, display_name, runtime, daily_slots_remaining}]` — registry view, ≤500 tokens total output for all 4 classes.
  - `agents_describe(class: str)` → full record from `agents.yaml` for one class.
  - `agents_handoff_plan(from_class, current_status)` → ordered list of `{to_class, trigger_match, suggested_payload}` proposals; empty list if no trigger matches (orchestrator-MUST-stop signal).
- [ ] `pytest -x tests/unit/agentic/test_agents_registry.py tests/unit/agentic/test_agent_handoff.py` exits 0. Tests cover: (a) valid manifest loads, (b) a broken fixture with a quota-zero entry fails with `AGENTS.QUOTA_INVALID`, (c) a broken fixture with `escalation_target: nonexistent` fails with `AGENTS.UNKNOWN_CLASS`, (d) a broken fixture with `A → B → A` cycle in `handoff_triggers` fails with `AGENTS.HANDOFF_CYCLE`, (e) `agents_handoff_plan("jules", "COMPLETED")` returns the codex-review trigger before the human-merge trigger.
- [ ] `docs/architecture/agent-role-manifest.md` (≤200 lines) describes the manifest's purpose, the four enumerated classes, the hand-off DAG diagram, and a worked example of the `jules → codex-review → human-merge` chain.
- [ ] `Plan/JULES_PROTOCOL.md` §6 (Escalation) gains one paragraph naming `agents.yaml` as the canonical lookup table for `escalation_target` and pointing at `agents_handoff_plan` as the runtime query primitive.
- [ ] `python Plan/_lint/check_affects.py Plan/136-agents-yaml-role-manifest/spec.md` exits 0 (validates this spec's own `affects:` enumeration via Spec 099's checker).

## Source clones (run first)

None — this spec is internal manifest authoring. `source-repos:` is `[]`. Read the existing handler shape in `servers/agency-mcp/src/agency_mcp/handlers/agentic/` (created by Spec 016) and follow the same `domain:agentic` tagging conventions.

## Files

- **Create**:
  - `agents.yaml` — the manifest (≤300 lines).
  - `state/schema/agents.schema.json` — JSON Schema for the manifest.
  - `Plan/_lint/check_agents_yaml.py` — schema + diagnostics linter.
  - `Plan/_lint/check_agent_handoff.py` — spec hand-off cross-checker.
  - `servers/agency-mcp/src/agency_mcp/handlers/agentic/agents_registry.py` — three MCP tools + YAML loader.
  - `tests/unit/agentic/test_agents_registry.py`, `tests/unit/agentic/test_agent_handoff.py`.
  - `tests/unit/agentic/fixtures/agents-valid.yaml`, `tests/unit/agentic/fixtures/agents-broken-quota.yaml`, `tests/unit/agentic/fixtures/agents-broken-cycle.yaml`.
  - `docs/architecture/agent-role-manifest.md`.
- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/handlers/agentic/__init__.py` — register the three new tools (append-only, no edits to existing tool registrations).
  - `Plan/JULES_PROTOCOL.md` — add `agents.yaml` reference under §6 (one paragraph; do not restructure existing sections).
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Confirm `agents.yaml` does not already exist (`ls agents.yaml 2>/dev/null`). Confirm `state/schema/` exists. Confirm Spec 099's `Plan/_lint/check_affects.py` has shipped (this spec depends on it). Cite Spec 099 PR sha + the 4 Plan slots already referencing agent classes (006, 007, 023, 099). Score ≥0.90 before any edit.
2. **Author `state/schema/agents.schema.json` first.** Define the JSON Schema (draft-2020-12) with `agents` as an array of objects, each carrying the fields enumerated in Done-When. Enums for `runtime`, `pr_authorship`, `closing_run_path` are closed sets. `handoff_triggers[].from_status` is a free-form string (per-agent-class state vocabulary varies).
3. **Author `agents.yaml`.** Four entries:
   - `jules` — runtime `cloud-async`, capabilities `[multi-file-refactor, test-generation, async-codegen]`, quota `daily_slots: 5, concurrent: 5, tokens_per_session: 200000`, `pr_authorship: true`, `closing_run_path: jules-finalize`, `escalation_target: codex-review`, handoff triggers `[{from_status: COMPLETED, to_class: codex-review, payload_shape: pr_url}, {from_status: AWAITING_PLAN_APPROVAL, to_class: local-orchestrator, payload_shape: plan_diff}]`.
   - `codex-review` — runtime `cloud-bot`, capabilities `[pr-comment-review, p1-p4-triage]`, quota `daily_slots: ~50, concurrent: 1, tokens_per_session: 30000`, `pr_authorship: bot-co-author`, `closing_run_path: n/a-comment-only`, `escalation_target: human`, handoff triggers `[{from_status: review_complete, to_class: jules, payload_shape: fix_directive}, {from_status: approve, to_class: human, payload_shape: merge_ready}]`.
   - `local-subagent` — runtime `local-subagent`, capabilities `[focused-codegen, ephemeral-research, pr-body-summarization]`, quota `daily_slots: unlimited, concurrent: 4, tokens_per_session: 100000`, `pr_authorship: false`, `closing_run_path: local-commit`, `escalation_target: local-orchestrator`, handoff triggers `[{from_status: complete, to_class: local-orchestrator, payload_shape: synthesis_summary}]`.
   - `local-orchestrator` — runtime `local-orchestrator`, capabilities `[multi-agent-coordination, watcher-supervision, friction-logging]`, quota `daily_slots: 1, concurrent: 1, tokens_per_session: 1000000`, `pr_authorship: true`, `closing_run_path: /sc:createPR`, `escalation_target: human`, handoff triggers `[]` (terminal — the orchestrator IS the dispatcher).
4. **Author `Plan/_lint/check_agents_yaml.py`.** Load the schema, load `agents.yaml`, run `jsonschema.validate()`, emit one diagnostic per failure. Run the cycle check via DFS on the `handoff_triggers` graph (each agent class is a node; each trigger is a directed edge to `to_class`). Exit 1 on any error, 0 on success.
5. **Author `Plan/_lint/check_agent_handoff.py`.** For each `Plan/*/spec.md`, parse frontmatter `owner:`. If `owner` is in `agents.yaml`, search the Approach section for the expected hand-off chain (e.g. `owner: jules` MUST mention `Codex` or `local-subagent review` somewhere in the body). Diagnostic `AGENTS.HANDOFF_MISSING`. Skip specs whose `domain:` is not in `{music, novel, jules, agentic, cross}` (no orphan-domain checks).
6. **Author `agents_registry.py` MCP handlers.** Three FastMCP tools (`@mcp.tool(tags={"domain:agentic"})`), all reading `agents.yaml` via a module-level `@lru_cache` loader. `agents_handoff_plan` does the trigger-graph lookup and returns a list (sorted by registry order). Each tool docstring ≤120 chars per overview §2.1.
7. **Modify `agentic/__init__.py`.** Append three `from .agents_registry import …` registration lines AT THE END of the file (per `server_py_edit: append-only` convention from Spec 099). Do not refactor existing imports.
8. **Author the docs page.** `docs/architecture/agent-role-manifest.md` — ≤200 lines, one Mermaid diagram of the four-class hand-off DAG, one worked example trace.
9. **Patch `Plan/JULES_PROTOCOL.md` §6.** Add ONE paragraph: "The `agents.yaml` manifest at repo root is the canonical lookup for `escalation_target`; query it at runtime via `agents_handoff_plan(from_class, current_status)` rather than hard-coding routes in spec prose."
10. **Gate 2 — TDD.** RED: write `test_agents_registry.py::test_valid_manifest_loads` against an empty handler — assert FAIL. GREEN: implement the loader. Repeat RED-GREEN for each anomaly fixture (quota-zero, cycle, unknown-class). REFACTOR: pull YAML parsing into a shared `_load_manifest()` helper if both lint scripts and the handler duplicate it.
11. **Gate 3 — Evidence.** Paste outputs of `pytest -x tests/unit/agentic/test_agents_registry.py`, `python Plan/_lint/check_agents_yaml.py`, `python Plan/_lint/check_agent_handoff.py`, `python -c "from agency_mcp.server import create_mcp; m=create_mcp(); print('agents_list' in m._tools)"`, and a sample `agents_handoff_plan("jules", "COMPLETED")` JSON result.
12. **Gate 4 — Self-Review + reviewer dispatch.** Answer the three Self-Review questions; dispatch the Gate-4 reviewer using `Plan/_templates/review-subagent-prompt.md` (created by Spec 099).

## Acceptance (Gherkin)

```gherkin
# anchor: 136.1
Scenario: A valid agents.yaml manifest passes the schema linter
  Given agents.yaml at repo root declares ≥4 agent classes with all required fields
  When the operator runs "python Plan/_lint/check_agents_yaml.py"
  Then the process exits with status 0
  And stdout reports the agent classes parsed and their handoff edge count

# anchor: 136.2
Scenario: A handoff cycle is caught at lint time
  Given a fixture manifest declares a handoff chain A → B → A
  When the operator runs "python Plan/_lint/check_agents_yaml.py path/to/fixture-cycle.yaml"
  Then the process exits with status 1
  And stderr contains the diagnostic "AGENTS.HANDOFF_CYCLE"
  And the diagnostic names the offending class pair

# anchor: 136.3
Scenario: agents_handoff_plan returns the correct successor for a Jules COMPLETED session
  Given the daemon is running with the canonical agents.yaml loaded
  When the orchestrator calls "agents_handoff_plan('jules', 'COMPLETED')"
  Then the response is a JSON list whose first element is {to_class: 'codex-review', trigger_match: 'COMPLETED', payload_shape: 'pr_url'}
  And the response is ≤ 800 tokens (measured by tiktoken)

# anchor: 136.4
Scenario: A spec owned by Jules but missing the codex-review hand-off mention is flagged
  Given a hand-crafted spec fixture declares "owner: jules" in frontmatter
  And its Approach section never mentions "Codex" or "local-subagent review"
  When the operator runs "python Plan/_lint/check_agent_handoff.py path/to/fixture-spec.md"
  Then the process exits with status 1
  And stderr contains "AGENTS.HANDOFF_MISSING"

# anchor: 136.5
Scenario: JULES_PROTOCOL.md §6 references the manifest
  Given the JULES_PROTOCOL.md patch from this spec has landed
  When the operator runs "rg -n 'agents.yaml' Plan/JULES_PROTOCOL.md"
  Then at least one match appears under §6 (Escalation)
  And the match cites "agents_handoff_plan" as the runtime primitive
```

## Out of scope

- **Per-agent authentication / credential storage.** `agents.yaml` is a declarative manifest, not a credential vault. Auth lives in environment-secret files (`~/.agency-system/secrets.yaml`), not here.
- **Dynamic quota refresh from cloud APIs.** `quota.daily_slots_remaining` in `agents_list()` is computed by Spec 100's session-log MCP at query time, not stored in the manifest. This spec only declares quota *limits*; the live counter is a separate Spec-100 concern.
- **Adding new agent classes (Devin, Aider, etc.) to the canonical four.** Future agent classes file their own ADR + supersession entry per `decisions/0011-external-skill-corpora-import.md` lineage; this spec only ships the four already in play.
- **Plugin-side enforcement of `agents.yaml` at tool-call time.** Runtime enforcement (e.g. "Jules cannot call music_master_album") is a future spec — this one ships the declarative manifest + lint-time gates only.
- **Spec 023's external MCP client validation.** Spec 023 validates that Cursor/Continue can speak the HTTP transport; this spec validates that the *agent identity* behind the call is one of the four registered classes. Adjacent, not overlapping.

## References

- `Plan/JULES_PROTOCOL.md` §6 (Escalation — the section this spec patches)
- `Plan/099-jules-orchestration-improvements/spec.md` — provides `Plan/_lint/check_affects.py` + `Plan/_templates/review-subagent-prompt.md` that this spec consumes
- `Plan/023-harness-in-harness/spec.md` — external-client surface that motivates a formal agent-class registry
- `Plan/100-session-log-mcp/spec.md` — owns the live quota counter referenced under "Out of scope"
- `Plan/101-jules-mcp-tool-additions/spec.md` — neighbouring `domain:agentic` handler conventions
- `Plan/_lessons-learned/05-independent-review-subagent-is-load-bearing.md` — empirical motivation for codifying the `jules → codex-review` hand-off
- `Plan/_lessons-learned/12-completed-without-pr-or-state-mismatch.md` — empirical motivation for explicit `closing_run_path` per agent class
- `Plan/_lessons-learned/13-codex-bot-pr-reviews-are-gold.md` — empirical motivation for elevating `codex-review` to a first-class agent
- `jules-plugin/skills/jules/references/parallel-orchestration.md` — the existing prose contract this manifest formalizes
- [Anthropic Skills: subagent role separation](https://platform.claude.com/docs/en/agents-and-tools/skills) — prior-art reference for declarative agent surfaces
