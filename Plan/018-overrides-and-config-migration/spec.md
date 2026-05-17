---
spec_id: 018
slug: overrides-and-config-migration
status: ready
owner: jules
depends_on: [015]
affects:
  - overrides/prose-style-guide.md
  - overrides/narrative-preferences.md
  - overrides/dramatica-defaults.md
  - overrides/ncp-defaults.md
  - config/agency-system.config.template.yaml
  - Plan/018-overrides-and-config-migration/references/config-diff.md
  - tests/unit/overrides/__init__.py
  - tests/unit/overrides/test_overrides_present.py
  - tests/unit/overrides/test_load_override.py
  - tests/unit/overrides/test_config_template.py
source-repos:
  - bitwize-music @ v0.91.0
estimated_jules_sessions: 1
domain: migration
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 018 — Overrides and Config Migration

## Why

bitwize-music ships a curated `overrides/` directory (lyric craft guide,
mastering presets, voice principles, pronunciation, suno preferences,
research preferences, promotion preferences, release preferences) that the
music skills load at session start via `shared_load_override`. The unified
plugin must extend that surface so the novel side has equivalent
craft-defaults — **without** rewriting the music overrides (already ported
in spec 005). Four novel overrides are missing today: `prose-style-guide.md`
(diction / register / pacing defaults), `narrative-preferences.md`
(POV / tense / narrator-distance defaults), `dramatica-defaults.md` (default
storyform quad + throughline assignment when the user hasn't authored one),
`ncp-defaults.md` (default `players[].motivations[]` / `players[].perspectives[]`
shape).

In parallel, bitwize's single user config template
(`bitwize-music.config.template.yaml`) must be merged into one unified
template (`agency-system.config.template.yaml`) with namespaced top-level
keys (`music`, `novel`, `jules`, `agentic`, `shared`). Spec 019 acts on the
*user's installed* config file; this spec produces the *template* that
seeds new installs and that spec 019 diffs against. The embedded
`references/config-diff.md` is the auditable record of every key migration.

## Done When

- [ ] All four novel override files exist with sensible default content (≥30 lines each, headed sections, no placeholders like `TODO`).
- [ ] `config/agency-system.config.template.yaml` exists, declares `version: "1.0.0"`, and contains top-level keys `music`, `novel`, `jules`, `agentic`, `shared` exactly once each.
- [ ] Every key present in `~/work/vendor/bitwize-music/config/bitwize-music.config.template.yaml` is reachable under `music.*` in the unified template — verified by the bash one-liner in `references/config-diff.md` §5.
- [ ] `shared_load_override("prose-style-guide")` returns the markdown body of `overrides/prose-style-guide.md` (relies on the `shared_load_override` tool delivered by spec 009).
- [ ] `shared_load_override("dramatica-defaults")` returns markdown containing the headings `## Default storyform quad` and `## Default throughline assignments`.
- [ ] `shared_load_override("ncp-defaults")` returns markdown containing the headings `## Default players[].motivations[]` and `## Default players[].perspectives[]`.
- [ ] `pytest -x tests/unit/overrides/` exits 0.
- [ ] `references/config-diff.md` exists, lists every preserved / renamed / new / removed key, and is referenced from this spec's `## References`.

## Source clones (run first)

```bash
git clone --depth=1 --branch=v0.91.0 \
  https://github.com/bitwize-music-studio/claude-ai-music-skills.git \
  ~/work/vendor/bitwize-music
```

`ls ~/work/vendor/bitwize-music/config/` should list at least
`bitwize-music.config.template.yaml`. `ls ~/work/vendor/bitwize-music/overrides/`
is for cross-reference of structure — do **not** copy files from there;
overrides were already ported in spec 005.

## Files

- **Create**:
  - `overrides/prose-style-guide.md` — sections: `## Diction defaults`, `## Register & cadence`, `## Pacing`, `## Sentence-length distribution`, `## Forbidden constructs (placeholder)`.
  - `overrides/narrative-preferences.md` — sections: `## POV defaults`, `## Tense defaults`, `## Narrator distance`, `## Free indirect style policy`, `## Showing vs telling guidance`.
  - `overrides/dramatica-defaults.md` — sections: `## Default storyform quad`, `## Default throughline assignments`, `## Resolve / Approach / Mental Sex / Growth defaults`, `## When to override these defaults`.
  - `overrides/ncp-defaults.md` — sections: `## Default players[].motivations[]`, `## Default players[].perspectives[]`, `## Default appreciations vocabulary`, `## Default narrative_functions ordering`.
  - `config/agency-system.config.template.yaml` — single unified template per `references/config-diff.md` §2–§3.
  - `tests/unit/overrides/__init__.py` + 3 test modules listed in `affects:`.
- **Modify**: none. The `shared_load_override` tool itself is unchanged.
- **Move / Delete**: none. The legacy `bitwize-music.config.template.yaml` is *not* copied into this repo — it lives only in the vendor tree.

## Approach

1. **Gate 1 — Confidence.** Confirm none of the four override files already exist (`ls overrides/prose-style-guide.md overrides/narrative-preferences.md overrides/dramatica-defaults.md overrides/ncp-defaults.md 2>&1`). Confirm `config/agency-system.config.template.yaml` does not yet exist. Confirm spec 009 has shipped `shared_load_override` (file `servers/agency-mcp/src/agency_mcp/handlers/shared/reference.py`). Confirm spec 015 has shipped enough of the novel skill catalogue that the override sections in §3 have downstream consumers (read the spec 015 affects list and cite the consumer skills). Cite all four commands in the PR `## Confidence` table.
2. **Clone bitwize.** Run the clone command. Read `vendor/bitwize-music/config/bitwize-music.config.template.yaml` end-to-end; enumerate every top-level key and every nested key into a flat list for the diff table.
3. **Author `references/config-diff.md` (already present).** The file at `Plan/018-overrides-and-config-migration/references/config-diff.md` is the source of truth for the unified template's shape. If during step 4 you discover a bitwize key not represented in §3.1, stop and update the diff file *first*; the diff is the contract.
4. **Author `config/agency-system.config.template.yaml`** strictly to the shape in `references/config-diff.md` §2 and §3:
   - `version: "1.0.0"` at top.
   - `music:` block contains every bitwize key from §3.1.
   - `novel:` block per §3.2 (paths to the four override files added in this spec).
   - `jules:` block per §3.3.
   - `agentic:` block per §3.4 (paths under `~/.agency-system/agentic/`).
   - `shared:` block per §3.5.
   - Inline comments at top of each block citing the source spec (e.g. `# music.* — preserved from bitwize-music.config.template.yaml v0.91.0 per Plan/018 references/config-diff.md §3.1`).
5. **Author the four novel override files.** Use the section headings listed under `Files`. Content rules:
   - Defaults must be opinionated but minimal — the user is expected to edit them.
   - Reference (don't duplicate) the dramatica / ncp library content shipped by spec 012; cite `lib/dramatica/` and `lib/ncp/` paths.
   - No placeholder text like `TODO` or `XXX` — every section is at least one complete sentence.
   - Frontmatter: `--- type: override domain: novel updated: <date> ---` minimal block at top of each file.
6. **TDD — Gate 2.** RED: write `test_overrides_present.py` (all four files exist + are non-empty + each contains its named section headings), `test_load_override.py` (mock or real `shared_load_override("prose-style-guide")` returns the body — defer to spec 009's helper), `test_config_template.py` (loads the YAML, asserts version key, asserts five top-level namespaces, runs the diff-script from `config-diff.md` §5 and asserts exit 0). Watch them fail. GREEN: author the files. REFACTOR: extract any duplication in test setup into a `_load_yaml` helper.
7. **Gate 3 — Evidence.** Paste in PR body: `pytest -x tests/unit/overrides/` last 20 lines, the verification one-liner from `references/config-diff.md` §5 with `echo exit=$?` showing `exit=0`, `ls -la overrides/` showing the four new files, a `head -5` excerpt of `overrides/dramatica-defaults.md` showing the named section headings.
8. **Gate 4 — Self-Review.** Answer the three questions. Specifically flag any bitwize key that resisted clean placement under `music.*` (with rationale), any opinion baked into the novel defaults that future users will want to override, and any section heading whose name was changed from the spec's `Files` list (with rationale).

## Acceptance (Gherkin)

```gherkin
# anchor: 018.1
Scenario: shared_load_override returns the body of a newly authored novel override
  Given overrides/dramatica-defaults.md has been authored per this spec
  And the shared handlers from spec 009 are registered on the FastMCP instance
  When the caller invokes shared_load_override(name="dramatica-defaults")
  Then the result envelope has ok=true
  And data is a markdown string containing the substring "## Default storyform quad"
  And data contains the substring "## Default throughline assignments"

# anchor: 018.2
Scenario: The unified config template covers every bitwize key under music.*
  Given config/agency-system.config.template.yaml has been authored per this spec
  And ~/work/vendor/bitwize-music/config/bitwize-music.config.template.yaml is available
  When the operator runs the verification one-liner from references/config-diff.md §5
  Then the script exits 0
  And no key name is printed to stdout

# anchor: 018.3
Scenario: The unified template declares the five expected top-level namespaces
  Given config/agency-system.config.template.yaml has been authored
  When the operator parses it as YAML
  Then the top-level keys include exactly: version, music, novel, jules, agentic, shared
  And the version value equals "1.0.0"

# anchor: 018.4
Scenario: All four novel override files exist with sensible defaults
  Given this spec has been applied
  When the operator runs `ls overrides/prose-style-guide.md overrides/narrative-preferences.md overrides/dramatica-defaults.md overrides/ncp-defaults.md`
  Then all four files are listed
  And each file is at least 30 lines long
  And no file contains the substring "TODO" or "XXX"
```

## Out of scope

- Migrating the user's *installed* `~/.bitwize-music/config.yaml` — that is spec 019.
- Authoring novel content beyond the override defaults (the actual novel skills live in spec 015).
- Modifying or renaming any existing override file ported by spec 005 — that surface is frozen.
- Deleting `~/work/vendor/bitwize-music/` or the bitwize plugin install — that is spec 020.
- Implementing `shared_load_override` — delivered by spec 009.
- Authoring `reference/` content that the new overrides cite — out of scope; the overrides cite paths even if the targets are stubs.

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §4 source-repo discipline)
- `Plan/000-overview.md` §1 (target tree — `overrides/` at root, `config/agency-system.config.template.yaml`), §2.1.10 (StateCache; the config file path it watches)
- `Plan/SOURCES.md` (bitwize-music v0.91.0 clone command)
- `Plan/018-overrides-and-config-migration/references/config-diff.md` (key-by-key migration table — authoritative)
- Spec dependency: `Plan/015-novel-skills-catalogue/spec.md` (novel skills that consume these overrides)
- Spec dependency: `Plan/009-shared-handlers/spec.md` (`shared_load_override` contract)
- Forward link: `Plan/019-state-migration-from-bitwize/spec.md` (acts on the *installed* config; this spec produces the *template* it migrates *to*)
- Vendor source (read-only): `~/work/vendor/bitwize-music/config/bitwize-music.config.template.yaml`
