---
spec_id: 015
slug: novel-skills-catalogue
status: ready
owner: jules
depends_on: [005, 011, 014]
affects:
  - skills/novel/**/SKILL.md
  - skills/novel/work-architect/SKILL.md
  - skills/novel/dramatica-theory/SKILL.md
  - skills/novel/dramatica-vocabulary/SKILL.md
  - skills/novel/ncp-author/SKILL.md
  - Plan/015-novel-skills-catalogue/references/parity-table.md
  - tools/skill_qc_lint.py
  - tests/unit/skills/__init__.py
  - tests/unit/skills/test_novel_skill_catalogue.py
source-repos:
  - agency @ claude/agency-plugin-refactor-PgMQ4
estimated_jules_sessions: 2
domain: novel
wave: B
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 015 — Novel Skills Catalogue

## Why

Skills are **the user interface** of a Claude Code plugin — they are the slash commands a human types and the agentic surface other skills reference. Spec 005 ports 54 music skills with parity and the L1+L2 frontmatter discipline; this spec authors the **28 spirit-isomorphic novel skills** (per the embedded parity brief — `prose-drafter`, `developmental-editor`, `line-editor`, `revision-engineer`, `copy-editor`, `proofreader`, `cover-art-director`, `pre-drafting-check`, `publication-director`, etc.) PLUS rebinds the **4 storyform/theory skills** from `agency/skills/` (`work-architect` ← `novel-architect`, `dramatica-theory`, `dramatica-vocabulary`, `ncp-author`). Without this spec, the novel handlers from Specs 011–014 and 021 exist but have no slash-command discovery surface — `/agency-system:novel-work-conceptualizer` doesn't resolve, the parity brief's editorial pipeline cannot be invoked, and the user has nothing to type. The 32 skills authored here turn the novel domain from "a Python package" into "a Claude Code product."

## Done When

- [ ] **32 SKILL.md files** exist under `skills/novel/`:
  - 28 spirit-isomorphic skills from the parity brief (see brief for the full list — the editorial stages, the QC family, the lifecycle family, the cover-and-promo family).
  - 4 ported storyform/theory skills: `work-architect`, `dramatica-theory`, `dramatica-vocabulary`, `ncp-author`.
- [ ] Each SKILL.md passes the **10-item Anthropic skill QC checklist** (overview §2.2):
  1. L1 Vault Core frontmatter present (`type: spec`, `status`, `slug`, `summary` ≤120 chars, `created`, `updated`)
  2. L2 `skill_*` namespace present (`skill_kind` ∈ 9-value enum, `skill_target_agents`, `skill_references_skills`, `skill_references_research`, `skill_references_prompts`, `skill_bootstrap_required`)
  3. `summary` is ≤120 chars
  4. `skill_kind` value is one of the 9 enum values
  5. Five mandatory body sections: `## What`, `## When to use`, `## How to use`, `## References`, `## Compatibility`
  6. Cross-refs to other skills appear *in frontmatter only*, not inline in body prose
  7. `:embed` suffix used only for composition, bare slug for invocation
  8. No `skill_referenced_by` field is authored (the linter computes reciprocity)
  9. All `skill_references_skills` entries resolve to an existing SKILL.md
  10. The file ends with a `## Compatibility` section listing the Claude Code version and MCP server version
- [ ] `tools/skill_qc_lint.py` exists and exits 0 when run as `python tools/skill_qc_lint.py skills/novel/`.
- [ ] `tests/unit/skills/test_novel_skill_catalogue.py` exits 0 with at least these tests: `test_count_is_32`, `test_all_pass_qc_lint`, `test_all_cross_refs_resolve`, `test_no_authored_referenced_by`.
- [ ] **Skill count delta**: after install, `/help | grep -c '/agency-system:'` increases by 32 vs the pre-spec baseline (verified by the smoke test reading the manifest).
- [ ] The 4 ported skills' `summary` field credits the agency repo and the source SKILL.md path (`Ported from agency/skills/<slug>/ — see references/parity-table.md`).
- [ ] `Plan/015-novel-skills-catalogue/references/parity-table.md` exists and is cited from each authored skill's `skill_references_research` frontmatter.

## Source clones (run first)

```bash
git clone --depth=1 --branch=claude/agency-plugin-refactor-PgMQ4 \
  https://github.com/netzkontrast/agency.git \
  ~/work/vendor/agency
```

For the 4 ported skills, the source directories live at:

- `~/work/vendor/agency/skills/novel-architect/` → port to `skills/novel/work-architect/`
- `~/work/vendor/agency/skills/dramatica-theory/` → port to `skills/novel/dramatica-theory/`
- `~/work/vendor/agency/skills/dramatica-vocabulary/` → port to `skills/novel/dramatica-vocabulary/`
- `~/work/vendor/agency/skills/ncp-author/` → port to `skills/novel/ncp-author/`

Also read `~/work/vendor/agency/skills/novel-architect-{scene,structure,world,character,legacy}/` for the sub-skill references that `work-architect` cross-references in frontmatter.

## Files

- **Create** (32 SKILL.md files — listed by family from the parity brief; full list in `references/parity-table.md`):
  - **Conceptualization & lifecycle (8)**: `novel-conceptualizer`, `new-work`, `premise-ideas`, `promote-premise`, `validate-work`, `import-cover`, `import-manuscript`, `import-chapter`.
  - **Drafting (3)**: `chapter-writer` (≡ prose-drafter), `prose-refiner` (≡ line-editor), `prose-reviewer` (≡ developmental-editor, 14-point QC).
  - **QC / Linting (5)**: `voice-consistency-checker`, `proper-noun-curator`, `pre-drafting-check` (wraps Spec 014 orchestrator, 6 BLOCKING gates), `plagiarism-checker`, `content-warning-checker` + `sensitivity-reader` (split from `explicit-checker`).
  - **Revision (3)**: `prose-revision-engineer` (multi-pass: structural → line → copy), `copy-editor`, `proofreader`.
  - **Cover & promo (4)**: `cover-art-director`, `book-promo-writer`, `book-promo-reviewer`, `book-promo-director`.
  - **Coordination (3)**: `publication-director` (9-domain QA gate), `work-dashboard`, `manuscript-coherence-check`.
  - **Pre-editorial human-feedback gates (2)**: `alpha-reader`, `beta-reader` (the parity brief's `Add` row).
  - **Ported from agency (4)**: `work-architect`, `dramatica-theory`, `dramatica-vocabulary`, `ncp-author`.
- **Create** (tooling):
  - `tools/skill_qc_lint.py` — a script that walks `skills/novel/`, parses YAML frontmatter, checks each of the 10 QC items, exits 0 on full pass and prints per-skill violations otherwise.
  - `tests/unit/skills/__init__.py` and `test_novel_skill_catalogue.py`.
- **Do not create**: the 10 prompt-builder skills — those are Spec 021. The parity brief explicitly carves the boundary: `skills/novel/<28+4 skills>/` vs `skills/novel/prompts/<10 builders>/`. Zero file overlap.

## Approach

1. **Gate 1 — Confidence (target ≥ 0.90).** Cite: `ls skills/novel/ 2>/dev/null` is empty (no duplicate); the 4 source skills exist in `~/work/vendor/agency/skills/`; Spec 014's `novel_run_pre_drafting_gates` is importable (`pre-drafting-check` will wrap it); Spec 005's lint tooling and skill QC discipline is already in place (`tools/skill_qc_lint.py` likely from Spec 005 — verify or author here); the parity brief in `references/parity-table.md` is current. Contract: 32 SKILL.md files that pass the 10-item QC and resolve all cross-refs.
2. **Read the parity brief end-to-end.** `references/parity-table.md` is the authority. The brief's 30-row table + 6 novel-specific additions + decisions section maps every authored skill to its music ancestor (or explicitly marks it `Add`/`Drop`/`Split`). Authoring deviates from the brief only via `[BLOCKED: clarification]`.
3. **TDD — Gate 2, RED.** Write `tests/unit/skills/test_novel_skill_catalogue.py` first with `test_count_is_32`, `test_all_pass_qc_lint`, `test_all_cross_refs_resolve`, `test_no_authored_referenced_by`. Run pytest — all 4 must fail (the skills don't exist yet). Paste the failing output into the PR.
4. **Author `tools/skill_qc_lint.py` (if not already from Spec 005).** Walk a directory; for each `SKILL.md`, parse YAML frontmatter with `pyyaml`; check items 1–10 against the overview §2.2 spec. Exit 0 on full pass; print per-skill `[FAIL item N]: <reason>` and exit 1 otherwise. The 10 checks are pure-functional — no I/O beyond reading the file — so each is a small `def check_item_N(frontmatter, body) -> tuple[bool, str]`.
5. **Port the 4 storyform/theory skills (verbatim-with-rebinding).** For each of `novel-architect → work-architect`, `dramatica-theory`, `dramatica-vocabulary`, `ncp-author`:
   - `cp -r ~/work/vendor/agency/skills/<source>/ skills/novel/<target>/`
   - Update `SKILL.md` frontmatter: change `slug:` to the new slug; update `summary` to credit the port; add `skill_references_research: ["Plan/015-novel-skills-catalogue/references/parity-table.md"]`; if the source has prerequisites referencing other agency skills not in this plugin, rewrite them to the in-plugin equivalents or remove with rationale; ensure `skill_kind` is set (the 9-value enum from overview §2.2).
   - For `work-architect`: cross-reference the 5 sub-skills (`novel-architect-scene`, `-structure`, `-world`, `-character`, `-legacy`) — if those are also being ported (decide via the parity brief), update slugs; if they are not, mark them as `skill_references_research` instead of `skill_references_skills`.
   - Run `python tools/skill_qc_lint.py skills/novel/work-architect/` and fix until exit 0.
6. **Author the 28 spirit-isomorphic skills.** For each parity-brief row marked `Keep` / `Add` / `Split`, author a SKILL.md with:
   - L1 frontmatter (mandatory 6 fields per overview §2.2).
   - L2 `skill_*` frontmatter (mandatory 6 fields). `skill_kind` chosen from the 9-value enum based on the row's role in the editorial pipeline (`domain` for drafting/editing skills, `orchestrator` for `pre-drafting-check` / `publication-director`, `persona` for the reader-feedback skills, `analysis` for the validators, etc.).
   - Body: 5 mandatory sections. `## What` = the parity-brief description verbatim. `## When to use` = the chain position from `CLAUDE.md`'s "pre-generation chain" / "pre-release chain" sections adapted to novels. `## How to use` = the MCP tool calls (from Specs 011/013/014/021) the skill orchestrates. `## References` = link to `references/parity-table.md` and to the originating music skill's path. `## Compatibility` = Claude Code version + `agency-mcp` server version.
   - Cross-refs in frontmatter only. Use `:embed` only when one skill literally embeds another's body; otherwise bare slugs.
7. **Resolve the cross-reference graph.** After all 32 skills are authored, run `python tools/skill_qc_lint.py skills/novel/` and check item 9 (all `skill_references_skills` resolve). Fix any dangling refs by either authoring the missing skill (if it's in the parity brief) or moving the ref to `skill_references_research` (if it points to a vendor-only skill).
8. **Programmatic QC.** Add a `test_all_qc_items_pass_per_skill` parametrized test that loops over every SKILL.md and asserts each of items 1–10 individually — gives per-item failure granularity rather than "the lint failed somewhere."
9. **Skill count delta verification.** Add `test_skill_count_delta_is_32` that reads the manifest (per Spec 002) and asserts the `/agency-system:` namespace gains exactly 32 entries vs a baseline counted from `git log -- skills/novel/ | wc -l` or similar — be precise about the baseline source.
10. **Gate 3 — Evidence.** Paste under `## Evidence`: (a) `pytest -x tests/unit/skills/test_novel_skill_catalogue.py` exit-zero tail, (b) `python tools/skill_qc_lint.py skills/novel/` exit-zero output, (c) `ls skills/novel/ | wc -l` showing 32, (d) sample `head -20 skills/novel/chapter-writer/SKILL.md` showing a well-formed frontmatter, (e) `grep -r 'skill_referenced_by' skills/novel/ | wc -l` showing 0 (item 8: linter computes reciprocity).
11. **Gate 4 — Self-Review.** Three questions. Specifically flag: any skill where the parity brief's role description proved ambiguous (e.g. `prose-revision-engineer` collapsing 3 music roles — is the collapse spec-compliant or does the brief need a footnote); any new `skill_kind` value invented (must not — the 9-value enum is closed); any skill that needed a body section beyond the 5 mandatory (e.g. a `## Prerequisites` chain — fine, but flag it).

## Acceptance (Gherkin)

```gherkin
# anchor: 015.1
Scenario: All 32 novel skills exist and pass the QC lint
  Given the catalogue has been authored per the parity brief
  When the operator runs "python tools/skill_qc_lint.py skills/novel/"
  Then the process exits with status 0
  And no per-skill violation is printed

# anchor: 015.2
Scenario: Skill cross-references resolve
  Given skills/novel/ contains 32 SKILL.md files
  When the linter checks each skill_references_skills entry
  Then every referenced slug resolves to an existing SKILL.md under skills/novel/ or skills/shared/
  And no skill authors a skill_referenced_by field (reciprocity is computed)

# anchor: 015.3
Scenario: Slash-command surface grows by exactly 32
  Given the plugin manifest from Spec 002
  And the baseline /agency-system: skill count prior to this spec
  When the manifest is reloaded after this spec ships
  Then the count of /agency-system:* skills increases by exactly 32

# anchor: 015.4
Scenario: Ported skills credit the agency repo
  Given the 4 ported skills (work-architect, dramatica-theory, dramatica-vocabulary, ncp-author)
  When their frontmatter is inspected
  Then each summary field contains the substring "Ported from agency/"
  And each skill_references_research field contains "Plan/015-novel-skills-catalogue/references/parity-table.md"

# anchor: 015.5
Scenario: pre-drafting-check skill wraps Spec 014's orchestrator
  Given skills/novel/pre-drafting-check/SKILL.md exists
  When the ## How to use section is inspected
  Then it documents a call to mcp.novel_run_pre_drafting_gates(work_id)
  And it documents the 6 BLOCKING gate names exactly as Spec 014 ships them
```

## Out of scope

- The 10 prompt-builder skills (Spec 021 — `skills/novel/prompts/`).
- Authoring new MCP handlers (Specs 011/013/014/021 own the handler surface; this spec is documentation + cross-refs).
- Music skill catalogue (Spec 005).
- Jules / agentic skill catalogue (Specs 007 / 016).
- Hooks integration (Spec 017).
- The plugin manifest itself (Spec 002 — this spec relies on the manifest auto-namespacing `skills/novel/<name>/` to `/agency-system:<name>`).
- State migration / cutover (Specs 018–020).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §4 source-repo discipline, §7 plugin specifics)
- `Plan/000-overview.md` §1 (target tree), §2.2 (skill QC checklist — items 1–10), §2.3 (skill auto-namespacing under `skills/<domain>/`)
- `Plan/SOURCES.md` (agency clone command)
- `Plan/015-novel-skills-catalogue/references/parity-table.md` — **the authoring brief this spec implements** (embedded from agent `a0c570a83e53508f8`)
- Spec dependency: `Plan/005-music-skills-port/spec.md` (the L1+L2 frontmatter discipline + `skill_qc_lint.py` tooling this spec reuses)
- Spec dependency: `Plan/014-novel-gates-and-revision/spec.md` (`pre-drafting-check` skill wraps `novel_run_pre_drafting_gates`)
- Spec downstream: `Plan/020-bitwize-deprecation-and-docs/spec.md` (cutover ensures novel + music skill catalogues are jointly resolvable)
- Spec sibling (not dependency): `Plan/021-novel-prompt-builder-family/spec.md` (the 10 prompt-builders live at `skills/novel/prompts/`, sibling family with zero overlap)
- Vendor source (read-only): `~/work/vendor/agency/skills/{novel-architect,dramatica-theory,dramatica-vocabulary,ncp-author}/SKILL.md` (the 4 ported skills)
- `/home/user/the-agency-system/CLAUDE.md` — pre-generation and pre-release chain descriptions that the QC and coordination skills adapt to novels
