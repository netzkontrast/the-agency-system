---
spec_id: 106
slug: github-mcp-summary-wrappers
status: ready
owner: jules
depends_on: [008, 016]
affects:
  - servers/agency-mcp/src/agency_mcp/handlers/agentic/__init__.py
  - servers/agency-mcp/src/agency_mcp/handlers/agentic/github_summary.py
  - servers/agency-mcp/src/agency_mcp/handlers/agentic/protos.py
  - tests/unit/agentic/__init__.py
  - tests/unit/agentic/test_github_summary.py
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

# Spec 106 — GitHub MCP Summary Wrappers (Subagent-Dispatched)

## Why

Per `Plan/_lessons-learned/14-token-consumption-postmortem.md`, `mcp__github__pull_request_read` is the **#1 token sink** in the entire system — a single call can return 40-80k tokens (full PR body, every file diff, every review comment, every commit). The main session almost never needs the raw payload; it needs a ~1-2k-token summary it can reason about. The fix is the Anthropic "effective context engineering" pattern: thin wrapper tools (`gh_pr_summary`, `gh_issue_summary`, `gh_review_summary`) dispatched as **ephemeral subagents** that call `mcp__github__*` in their own isolated context, distil the response, and return typed Pydantic protos (`PRSummary`, `IssueSummary`, `ReviewSummary`). Expected saving: **85-95% on every PR/issue read**.

## Done When

- [ ] `agency_mcp.handlers.agentic.protos.PRSummary`, `IssueSummary`, `ReviewSummary` Pydantic models exist with fields documented in §Approach.
- [ ] `gh_pr_summary(owner, repo, pr_number)` is registered as an MCP tool that spawns a subagent and returns `PRSummary`.
- [ ] `gh_issue_summary(owner, repo, issue_number)` returns `IssueSummary`.
- [ ] `gh_review_summary(owner, repo, pr_number, review_id)` returns `ReviewSummary`.
- [ ] Each subagent is dispatched with an explicit allow-list of MCP tools (only the `mcp__github__*` calls it needs) and a max-tokens cap on its summary output (target ≤ 2000 tokens).
- [ ] `pytest -x tests/unit/agentic/test_github_summary.py` exits 0 (uses recorded subagent fixtures, no live GitHub calls).
- [ ] Token-budget regression: integration smoke asserts `PRSummary` serialised size is ≤ 2500 bytes for a sample PR whose raw `pull_request_read` exceeds 40k tokens.

## Source clones (run first)

None — this spec consumes the `mcp__github__*` tools already exposed by the GitHub MCP server, and follows the Anthropic engineering pattern documented in the reference URL. No third-party vendor code.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/handlers/agentic/__init__.py` — extends Spec 016's agentic package with `register_github_summary_handlers(mcp)`.
  - `servers/agency-mcp/src/agency_mcp/handlers/agentic/github_summary.py` — three wrapper tools + subagent dispatch.
  - `servers/agency-mcp/src/agency_mcp/handlers/agentic/protos.py` — `PRSummary`, `IssueSummary`, `ReviewSummary` Pydantic models.
  - `tests/unit/agentic/__init__.py`.
  - `tests/unit/agentic/test_github_summary.py` — proto schema + subagent contract + token-budget regression.
- **Modify**: none — registration is wired through `handlers/agentic/__init__.py`, which Spec 016 already imports.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 008 (codemode registry) and Spec 016 (agentic handlers scaffolding) have shipped. Confirm the subagent dispatch primitive (`agency_mcp.lib.codemode.subagent.spawn(...)` from Spec 016) accepts a tool allow-list and a max-tokens cap. Read the Anthropic reference to confirm the proto-summary contract.
2. **Define the protos.** In `protos.py`, declare `PRSummary` with fields: `number: int`, `title: str`, `state: Literal["open","closed","merged"]`, `author: str`, `head_ref: str`, `base_ref: str`, `files_changed: int`, `additions: int`, `deletions: int`, `summary: str` (≤ 800 chars distilled body), `key_review_threads: list[str]` (≤ 5 quoted blockers), `mergeable: bool | None`. `IssueSummary`: `number`, `title`, `state`, `author`, `labels: list[str]`, `summary: str`, `linked_prs: list[int]`. `ReviewSummary`: `id`, `reviewer`, `state: Literal["approved","changes_requested","commented"]`, `summary: str`, `blocking_comments: list[str]`.
3. **Implement `gh_pr_summary`.** The handler builds a subagent prompt that instructs the ephemeral agent to: call `mcp__github__pull_request_read` once, call `mcp__github__list_commits` once, call `mcp__github__pull_request_review_write` only for read-side use cases (none here — read-only), distil into the `PRSummary` schema, and return JSON matching the proto. Cap the subagent at 6 tool calls and 2000 output tokens. Validate the returned JSON via `PRSummary.model_validate(...)`.
4. **Implement `gh_issue_summary` and `gh_review_summary`.** Same pattern, scoped allow-lists: issue uses `issue_read` + `add_issue_comment` (read only), review uses `pull_request_read` + `add_comment_to_pending_review` (read only — never write). Each builds the matching proto.
5. **Tag and register.** Tag all three tools with `tags={"domain:agentic", "subagent:true"}`. Register them inside `register_github_summary_handlers(mcp)`, called from `handlers/agentic/__init__.py:register_agentic_handlers(mcp)`.
6. **Defensive contracts.** If the subagent returns invalid JSON or exceeds the token cap, raise `SubagentSummaryError` with the raw output truncated to 400 chars; do **not** fall through to a raw `pull_request_read` (that would defeat the savings). Document the error path in module docstrings.
7. **TDD — Gate 2.** RED: write `test_github_summary.py` with four tests: each proto round-trips through `model_validate`, the `gh_pr_summary` handler dispatches a subagent with the correct allow-list (fixture-mocked), the byte-size regression for a recorded 40k-token PR fixture, the `SubagentSummaryError` path. Run — must fail.
8. **GREEN.** Implement the three handlers + protos. Wire them through `register_github_summary_handlers`. Re-run; tests pass.
9. **REFACTOR.** Extract the prompt-building boilerplate into `_build_summary_prompt(model_cls, instructions, allow_list)`. Confirm no handler accepts arbitrary user-supplied tool names in its allow-list (`rg 'allow_list' servers/agency-mcp/src/agency_mcp/handlers/agentic/`).
10. **Gate 3 — Evidence.** Paste pytest output, the byte-size assertion delta (raw PR fixture vs `PRSummary` serialised size), and a redacted sample `PRSummary` JSON in PR `## Evidence`. **Gate 4 — Self-Review.** Flag any fields intentionally omitted from the protos (e.g. full diff hunks) with rationale.

## Acceptance (Gherkin)

```gherkin
# anchor: 106.1
Scenario: gh_pr_summary returns a typed PRSummary smaller than 2500 bytes
  Given a PR whose raw mcp__github__pull_request_read response exceeds 40000 tokens
  When the caller invokes gh_pr_summary(owner="bitwize-music-studio", repo="claude-ai-music-skills", pr_number=42)
  Then the response is a valid PRSummary Pydantic model
  And the serialised JSON length is <= 2500 bytes
  And the response.summary field length is <= 800 characters

# anchor: 106.2
Scenario: gh_issue_summary subagent dispatches with a scoped allow-list
  Given the subagent dispatch primitive records its allow_list parameter
  When the caller invokes gh_issue_summary(owner="o", repo="r", issue_number=1)
  Then the subagent allow_list contains "mcp__github__issue_read"
  And the subagent allow_list does NOT contain "mcp__github__issue_write"
  And the subagent allow_list does NOT contain any non-github tool

# anchor: 106.3
Scenario: gh_review_summary returns ReviewSummary with blocking comments distilled
  Given a PR review with 12 comment threads where 3 are blocking
  When the caller invokes gh_review_summary(owner="o", repo="r", pr_number=42, review_id=99)
  Then the response.state is one of {"approved", "changes_requested", "commented"}
  And the response.blocking_comments has length <= 5
  And every blocking comment is <= 240 characters

# anchor: 106.4
Scenario: Invalid subagent output raises SubagentSummaryError without falling back to raw read
  Given the subagent returns malformed JSON
  When the caller invokes gh_pr_summary(...)
  Then a SubagentSummaryError is raised
  And no call is made to mcp__github__pull_request_read from the main session
```

## Out of scope

- Caching of `PRSummary` results across sessions (future spec — would need invalidation on push events).
- Write-side wrappers (`gh_pr_comment_summary`, etc.) — Wave C focuses on the read sinks only.
- Migrating callers to use the wrappers — Spec 016 + downstream skills will switch over as a follow-up.
- Direct GitHub REST/GraphQL access — we strictly route through `mcp__github__*`.

## References

- Anthropic — "Effective context engineering for AI agents": https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- `Plan/_lessons-learned/14-token-consumption-postmortem.md` §1 (top sinks — `pull_request_read` is #1)
- `Plan/JULES_PROTOCOL.md` (gates 1–4)
- `Plan/000-overview.md` §2.5 (agentic handlers + subagent dispatch)
- Spec dependency: `Plan/008-codemode-registry/spec.md` (registry hook for `subagent:true` tag)
- Spec dependency: `Plan/016-agentic-handlers-and-skills/spec.md` (subagent dispatch primitive + agentic package root)
