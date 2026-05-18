---
type: audit
authored: 2026-05-18
session: spec-hygiene-pass
scope: frontmatter of 32 ready specs in Plan/
related_pr: claude/spec-hygiene-pass-CtdIJ → Master
---

# Spec hygiene audit — 2026-05-18

## What this is

A one-shot pass over the 32 `status: ready` specs in `Plan/` (after Wave-A
landed via PRs #30 and #46), looking for three categories of defect:

1. **Architectural drift** — `affects:` paths that no longer exist on
   Master post-Wave-A, or that contradict where the file actually
   lives.
2. **BCP-14 gap** — `## Acceptance (Gherkin)` blocks whose normative
   sentences use non-normative language (no MUST / SHOULD / MAY) where
   a hard requirement is clearly intended.
3. **Cross-spec contradiction** — frontmatter that disagrees with the
   master `Plan/000-overview.md` table or with another spec's stated
   contract.

Scope discipline (from the move-2 brief):
- Frontmatter patches only — no body rewrites.
- No `status` flips.
- No new specs.
- No edits to `Plan/JULES_PROTOCOL.md` or `Plan/000-overview.md`.

The PR carrying this audit contains exactly **two** frontmatter patches
(both architectural-drift / stale-path defects with unambiguous
evidence) plus this audit document. Everything else is flagged below
for a follow-up session.

## Summary

| Defect category | Specs flagged | Specs patched in this PR |
|---|---:|---:|
| Architectural drift (stale `affects:` paths) | 2 | 2 |
| Stale `source-repos: agency @ claude/agency-plugin-refactor-PgMQ4` | 4 | 0 |
| BCP-14 gap (low / zero MUST-SHOULD-MAY density in Gherkin) | 31 | 0 |
| Cross-spec / overview contradictions | 4 | 0 |
| Frontmatter style inconsistency (cosmetic) | 2 | 0 |

Patched specs: **011a, 098**.

Audit-only flagged specs (no patch, evidence below): **003, 015, 016,
020, 021, 023, 100, 107**, plus the systemic BCP-14 finding across
~all ready specs.

---

## Patched in this PR

### 011a — `novel-handlers-core-hardening` (status: ready, wave: B)

- **Defect category:** architectural drift.
- **Evidence:** frontmatter `affects:` line cited
  `servers/agency-mcp/src/agency_mcp/handlers/novel/novel_indexer.py`.
  The novel indexer was landed by Spec 011 / 003 at
  `servers/agency-mcp/src/agency_mcp/state/indexers/novel_indexer.py`.
  The `handlers/novel/` directory contains no `novel_indexer.py`:
  ```text
  servers/agency-mcp/src/agency_mcp/handlers/novel/
    characters.py  coherence.py  content.py  core.py
    ideas.py       prose_analysis.py  status.py
    structure.py   work_ops.py  world.py
  ```
  The actual indexer lives at:
  ```text
  servers/agency-mcp/src/agency_mcp/state/indexers/novel_indexer.py
  ```
- **Patch applied:** frontmatter line repointed to
  `servers/agency-mcp/src/agency_mcp/state/indexers/novel_indexer.py`.
- **Residual defect (NOT patched, out-of-scope for hygiene PR):**
  the spec **body** (line 63) repeats the wrong path inside the
  Approach section. A separate per-spec session must update the body
  before dispatch. Flagged for the orchestrator.

### 098 — `wave-a-hardening` (status: ready, wave: A)

- **Defect category:** architectural drift.
- **Evidence:** frontmatter `affects:` line cited
  `servers/agency-mcp/src/agency_mcp/state/migrators/bitwize_v091_to_agency.py`.
  Spec 019 (done, on Master) landed the migrator at the **repo-root**
  path `state/migrators/bitwize_v091_to_agency.py`. Verified:
  ```text
  state/migrators/
    __init__.py  _atomic.py  _hashing.py
    bitwize_v091_to_agency.py
  ```
  And no `migrators/` directory exists under
  `servers/agency-mcp/src/agency_mcp/state/`.
  The spec's body uses both paths inconsistently — line 9
  (frontmatter, now patched) and line 73 (body, NOT patched) said
  the wrong path; line 46 (body, untouched) already says the right
  path. The body therefore already disagrees with itself.
- **Patch applied:** frontmatter line repointed to
  `state/migrators/bitwize_v091_to_agency.py`.
- **Residual defect (NOT patched, out-of-scope):** body line 73
  still cites the wrong path. Flagged for the orchestrator.

---

## Flagged but NOT patched

### Stale `source-repos: agency @ claude/agency-plugin-refactor-PgMQ4`

Specs **015, 016, 020, 021** (all `status: ready`) include a
`source-repos:` entry pointing at the now-defunct Wave-A staging
branch `claude/agency-plugin-refactor-PgMQ4`.

- **Defect category:** architectural drift.
- **Evidence:** per `Plan/JULES_PROTOCOL.md` §3, that branch "was
  the staging area for Wave A — it still exists on remote, identical
  to Master tip, but new sessions should target Master directly."
  The git-clone command still resolves (the branch is alive), so the
  clone is not strictly broken — but the convention is dead. The
  spec **body** of each of these four specs also contains a
  `git clone --depth=1 --branch=claude/agency-plugin-refactor-PgMQ4 …`
  command in its Approach section. Patching only the frontmatter
  while leaving the body command intact would create an internal
  contradiction worse than the original drift.
- **Why no patch in this PR:** the body change is out of scope. The
  fix needs to land as part of a single coordinated edit per spec.
- **Recommended follow-up:** in a separate per-spec session, change
  both the frontmatter entry and the body's clone command to
  `agency @ Master`, OR drop the `source-repos: agency …` line
  entirely (the agency repo is the *current* repo — cloning it into
  `~/work/vendor/` is redundant on a fresh Jules sandbox that
  already has the repo checked out).

### BCP-14 gap — Gherkin acceptance criteria use non-normative language

Across all 32 ready specs, the `## Acceptance (Gherkin)` blocks
overwhelmingly use plain declarative English ("the server returns",
"the indexer rebuilds", "the file exists") rather than RFC-2119 /
BCP-14 keywords. Concrete counts (raw `MUST|SHOULD|MAY` matches per
file, body + frontmatter combined):

```
0 keywords: 011a, 015, 016, 017, 018, 020, 021, 022, 098, 100, 101,
            102, 103, 104, 105, 106, 107, 108, 116, 120
1 keyword:  014, 099, 112, 115, 118, 119, 121
2 keywords: 023, 111, 113, 114, 117
```

- **Defect category:** BCP-14 gap.
- **Evidence sample (Spec 022, dev-mode-install, 0 keywords):**
  the Done-When list includes contracts like "`claude --plugin-dir`
  loads the in-progress plugin in under 5 minutes" — a hard
  performance ceiling stated in declarative future tense. A normative
  reading would be: "the plugin MUST load within 5 minutes of
  invocation under `claude --plugin-dir`".
- **Why no patch in this PR:** the brief explicitly forbids
  Gherkin rewrites here. This is a body-level concern and needs
  a coordinated authoring pass, ideally against a shared style
  guide (e.g. Plan/_templates/spec-template.md, which Spec 099 is
  scheduled to create).
- **Recommended follow-up:** when Spec 099
  (jules-orchestration-improvements) ships its
  `Plan/_templates/spec-template.md`, codify BCP-14 usage there and
  back-fill the 31 ready specs in a follow-up hygiene pass.

### Cross-spec / overview contradictions

#### Spec 023 not listed in `Plan/000-overview.md`

- **Evidence:** `Plan/000-overview.md` says "46 specs as of 2026-05-18"
  but `find Plan -maxdepth 2 -name spec.md` returns 47 specs.
  Spec 023 (harness-in-harness, `status: ready`, `wave: B`,
  `spec_kind: research_epic`) is not in any wave table in the
  overview, nor in the dependency DAG, nor in the recommended
  dispatch order.
- **Defect category:** cross-spec contradiction (overview is master
  doc, spec exists outside it).
- **Why no patch in this PR:** `Plan/000-overview.md` is on the
  do-not-touch list per the brief.
- **Recommended follow-up:** in the next orchestration-handoff cycle,
  add a row for 023 to the appropriate wave table (`Wave B remaining`
  or a new "Research epics" section), update the spec count, and
  decide whether 023 sits on the v1.0 critical path or is a
  post-v1.0 epic.

#### Spec 100 `wave: C` vs. shallow dependencies

- **Evidence:** `100-session-log-mcp` declares `wave: C` but
  `depends_on: [001]` — and 001 is done. By dependency depth alone
  it could ship as soon as Wave-B opens (or even earlier). Several
  Wave-B specs depend on 100 (118, 119, 120 list 100 as a dep), so
  scheduling 100 in Wave C actually blocks its own consumers if
  they ship first.
- **Defect category:** cross-spec contradiction.
- **Why no patch in this PR:** changing `wave: C` → `wave: B` is a
  scheduling decision, not a hygiene defect — needs the orchestrator
  to confirm intent.
- **Recommended follow-up:** flip to `wave: B` if the consumers
  (118/119/120) really need it earlier; otherwise demote the
  consumers to Wave C. Either way the current state is contradictory.

#### Spec 107 `wave: C` inconsistent with cluster

- **Evidence:** the "Token-efficiency" cluster (Specs 103-107) all
  depend only on Spec 008 (done). Specs 103, 104, 105 declare
  `wave: B`; Specs 106, 107 declare `wave: C`. Spec 106's choice
  is defensible (it also `depends_on: 016` which is Wave C), but
  Spec 107 depends only on 008, just like 103-105 — its `wave: C`
  label is inconsistent with the rest of the cluster and with the
  overview's "Token-efficiency" grouping (which assigns no
  explicit wave to any of 103-107).
- **Defect category:** cross-spec contradiction.
- **Why no patch in this PR:** as with 100, this is a scheduling
  choice the orchestrator should affirm before flipping. The wave
  field is load-bearing for dispatch order.
- **Recommended follow-up:** decide cluster-wide. Either move 107 to
  `wave: B` to match 103/104/105, or move all of 103-105 to `wave: C`.

### Frontmatter style inconsistency (cosmetic)

#### Spec 003 `source-repos:` separator

- **Evidence:** Spec 003 has
  `- bitwize-music: v0.91.0` (colon — parses as a YAML mapping,
  `{bitwize-music: "v0.91.0"}`). Every other spec citing the
  bitwize source uses `- bitwize-music @ v0.91.0` (string with `@`
  separator). The colon-form is still parseable, so this is a style
  defect not a correctness defect — but it breaks any frontmatter
  linter that expects all `source-repos:` entries to share a type.
- **Why no patch:** Spec 003 is `status: done` (merged). The brief
  allows frontmatter patches to merged specs only "if defective".
  Cosmetic-only mismatch falls below that bar.
- **Recommended follow-up:** roll this into a future frontmatter-
  lint pass once Spec 099's `Plan/_lint/check_affects.py` exists.

#### `deps:` key is non-universal

- **Evidence:** Specs 004a (`deps: []`) and 012
  (`deps: [jsonschema>=4.21.0]`) declare a `deps:` frontmatter key
  that no other spec uses. `JULES_PROTOCOL.md` §5 anti-pattern 5
  references `deps:` as the canonical place for added build/runtime
  deps, so the key is sanctioned but under-adopted.
- **Why no patch:** adding empty `deps: []` to 30+ specs would be
  noise; this is better solved by codifying the key in the spec
  template (Spec 099 task).

---

## Items requiring a separate spec (not hygiene-fixable)

These are systemic patterns that surfaced during the audit but are
out of scope for any spec-patching PR. Recording here so the
orchestrator can decide whether to commission new specs.

1. **Spec template + frontmatter linter.** Spec 099 already covers
   this surface (it lists `Plan/_lint/check_affects.py` and
   `Plan/_templates/spec-template.md` in its `affects:`). Strongly
   recommend dispatching 099 before any further hygiene work — a
   linter would have caught both patches in this PR automatically.
2. **Wave-field semantics.** The `wave:` key currently mixes "what
   wave the work block belongs to" (planning sense) with "what wave
   it can be dispatched in" (scheduling sense). The 100/107
   contradictions stem from this conflation. A short ADR clarifying
   the semantics (and possibly splitting into `wave_planned:` vs
   `wave_dispatchable:`) would prevent recurrence.
3. **`source-repos: agency @ …` self-clones.** Four ready specs
   instruct Jules to clone the agency repo into `~/work/vendor/`,
   but Jules's sandbox already has the repo checked out at the
   working directory. The clone is wasted work and produces a
   second copy that can drift. A protocol clarification ("never
   self-clone the current repo") would let those four specs drop
   the line entirely.

## Specs touched by this PR (table)

| Spec ID | Status | Defect | Patch |
|---|---|---|---|
| 011a | ready | `handlers/novel/novel_indexer.py` doesn't exist; indexer lives at `state/indexers/novel_indexer.py` | repointed frontmatter `affects:` line |
| 098 | ready | `servers/agency-mcp/src/agency_mcp/state/migrators/` doesn't exist; migrator lives at `state/migrators/bitwize_v091_to_agency.py` | repointed frontmatter `affects:` line |

## Reproduction commands

For the orchestrator (or a future hygiene session) to re-verify the
two patches:

```bash
# 011a — confirm indexer location
find servers/agency-mcp/src/agency_mcp -name "novel_indexer*"
# expected: servers/agency-mcp/src/agency_mcp/state/indexers/novel_indexer.py
# UNexpected: anything under handlers/novel/

# 098 — confirm migrator location
find . -name "bitwize_v091_to_agency.py" 2>/dev/null
# expected: ./state/migrators/bitwize_v091_to_agency.py
# UNexpected: anything under servers/agency-mcp/src/agency_mcp/state/
```

End of audit.
