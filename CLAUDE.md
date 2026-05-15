# the-agency-system — Claude Code instructions

## Four mantras

1. **Skills before MCP** — invoke `/bitwize-music:<skill>` first. MCP tools are primitives skills build on; call them directly only when a skill explicitly delegates to one.
2. **Tools before handcrafting** — if a tool owns the field, use it (`update_track_field`, `create_track`, `rebuild_state`, `load_override`). Before reaching for Edit, ask: "is there a tool for this?"
3. **Subagents by default** — parallel, independent, or context-heavy work goes to subagents. Delegate: parallel research, content locating (`Explore` subagent), 5+ file analysis, independent drafts, audits.
4. **Journal discipline** — invoke `Skill('journaling')` at session start. Record insights mid-session. Close every session with `process_thoughts`. See `.claude/skills/journaling/SKILL.md`.

## Hard gates (binding when the skill is invoked)

- **Concept phase** — `album-conceptualizer` Phase 7 (Confirmation) must complete before `lyric-writer` runs. Partial agreement triggers revision, not a forward pass.
- **Documentary sources** — every track must reach `sources_verified = Verified (date)` before `lyric-writer` runs. Non-documentary albums: `N/A` is acceptable.
- **Pre-generation** — `pre-generation-check` runs 6 BLOCKING gates (sources, lyrics, pronunciation, explicit, style box, artist names). Optional to invoke; binding when invoked.
- **Release** — `release-director` runs a 9-domain QA gate. Optional to invoke; blocks until all domains pass when invoked.

## Handoff reminder (mandatory after every skill)

End each skill reply with: *"Next step (optional): `/bitwize-music:<skill>` would [one sentence]. Run it, or proceed?"* User decides — never auto-invoke.

When unsure what's next, invoke `/bitwize-music:resume <album>` or `/bitwize-music:next-step` rather than guessing.

## Overrides vs album content

`overrides/` holds **cross-project** preferences only: taste, lexicon avoidances, genre→Suno mappings, vocal-register defaults, mastering presets, source-priority standards.

Album-specific content lives in the album folder — never in `overrides/`:
- Alter/character DNA → `<album>/cast.md` or `<album>/the-eleven.md`
- Narrative / arc → `<album>/README.md`
- Per-track pronunciations → the track file's Pronunciation Notes table
- Research / sources → `<album>/RESEARCH.md`, `<album>/SOURCES.md`

## Repository essentials

- `artists/<artist>/albums/<genre>/<slug>/` — album content
- `overrides/` — cross-project preferences (auto-loaded at session start)
- `audio/`, `documents/` — Git LFS (`git lfs install` once per machine)
- **Default branch: `Master`** (capital M). All PRs target `Master`. Passing `base: main` to `create_pull_request` returns 422.

## Session start (fresh session or project switch)

1. `Skill('journaling')` — recover context from prior sessions (tag search, recent briefs).
2. `/bitwize-music:health-check` — verify plugin + MCP stack.
3. Spot-check `overrides/` for stale project-specific content before invoking skills that load them.
