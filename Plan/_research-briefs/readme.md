# Research Briefs (Jules dispatch artefacts)

Each `NN-<slug>.md` in this folder is the verbatim prompt body of a Jules research session that was dispatched via `jules-plugin/bin/jules-bulk fanout`. The brief lives in the repo so the dispatch is auditable, reproducible, and supersession-safe (edit only by adding a new brief that references the prior one).

## Convention

- Frontmatter declares: `type: research-brief`, `status: dispatched|superseded`, `dispatched_to: jules`, `dispatched_at`, `parent_specs`, `output_branch`, `output_files`.
- Body is the literal prompt sent to Jules. Includes goal, required reading, source-clone commands, output paths, acceptance criteria, and anti-patterns.
- Research output lands on the declared `output_branch` (Jules's own branch off `Master`) — never on the brief's host branch.
- Findings + draft specs land under `Plan/_research/<slug>/` so they do not collide with numbered Plan specs until promoted.

## Dispatch log

| # | Slug | Dispatched | Session ID | Status | Output |
|---|---|---|---|---|---|
| 01 | centralized-ontology | 2026-05-18 | [13927980186995922904](https://jules.google.com/session/13927980186995922904) | dispatched + rebase-msg sent | `Plan/_research/centralized-ontology/` |
| 02 | agency-tooling-codemode | 2026-05-18 | [18243598847213256634](https://jules.google.com/session/18243598847213256634) | dispatched + rebase-msg sent | `Plan/_research/agency-tooling-codemode/` |
| 03 | graphqlite-codemode | 2026-05-18 | [10708258290716043154](https://jules.google.com/session/10708258290716043154) | dispatched + rebase-msg sent | `Plan/_research/graphqlite-codemode/` |

**Note (2026-05-18):** All sessions were initially created with `starting_branch=Master`. A follow-up `jules_message` was sent to each session instructing them to fetch `claude/document-context-mode-specs-qX8h7` and branch their work from there (so output PRs target this branch, not Master). For session 03, the immediate `jules_message` returned 404 — retried after 5 s once the session reached `IN_PROGRESS`. Verify on first plan-approval that Jules adopted the rebase before approving.

**Note (2026-05-18, fixed):** ~~`jules-plugin/bin/jules-bulk fanout` has a known shim bug — it imports `jules_create` from `jules_mcp.server` but the function lives in `jules_mcp.tools.lifecycle`.~~ Fixed in commit `<this branch>` — all four shim heredocs (`fanout`, `dashboard`, `approve-awaiting`, `quota`) now import from `jules_mcp.tools.lifecycle` / `jules_mcp.tools.bulk` directly. Smoke-tested: `jules-bulk quota` and `jules-bulk dashboard` work end-to-end.

**Note (2026-05-18, fixed):** ~~`jules_message` returns 404 on a session that is still in initial setup~~ Fixed in commit `<this branch>` — `jules_create` now accepts an `initial_messages: list[str] | None = None` parameter. Each entry is sent via `:sendMessage` after the session is created, with built-in exponential-backoff retry on 404 (up to 6 attempts, capped at 30 s per backoff). Non-404 errors do not retry; failures are recorded as `initial_messages_failed: [{message, status, attempts}]` on the response without raising. The fanout JSON entry schema also accepts `initial_messages: [...]` so the rebase-onto-branch instruction is part of a single fan-out call.

## How to fan out a new brief

1. Author the brief in this folder following the existing template.
2. Append to `fanout.json` (or generate a fresh fanout file from the briefs via `tools/jules/build-fanout.py` if/when that lands).
3. Run from repo root: `CLAUDE_PLUGIN_ROOT=$(pwd)/jules-plugin ./jules-plugin/bin/jules-bulk fanout Plan/_research-briefs/fanout.json`
4. Capture session IDs into `fanout-log.txt`.
5. Update the dispatch log table above.

## Supersession rule

Never edit a brief in place once dispatched. To revise: add `NN+1-<slug>.md` with frontmatter `supersedes: NN-<slug>.md` and flip the prior brief's status to `superseded`.
