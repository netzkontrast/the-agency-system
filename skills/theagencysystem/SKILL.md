---
name: the-agency-system
description: >
  Loads the cross-layer DNA (voice, arousal-state, visual grammar) for the
  artist/project "the Agency System" — a DID-system concept that spans music,
  a novel, and a visual design language. Use when starting or continuing any
  work on the Agency System (an album, a lyric, a Suno prompt, cover art, or a
  novel chapter), and whenever a bitwize-music skill is about to run for this
  artist. Gates first on "Is the artist/project the Agency System?"; if yes,
  loads ONLY the snippets needed for the active (function × state × layer).
argument-hint: '[function|name] [state S0-S4] [layer: music|novel|design]'
allowed-tools:
  - Read
  - Grep
  - AskUserQuestion
---

## What this skill is

A **gate + loader** for the Agency System's DNA. The cast and the world are
one model expressed in three layers — **music**, **novel**, **design** — joined
by a 2D matrix `function × state`. This skill asks whether you are really
working on the Agency System, then pulls the minimum DNA into whatever bitwize
(or novel) process is running. It never loads more than the active cell needs.

**Quick start:** (1) ask the gate question; (2) on *Yes*, read
[`references/resolver.yaml`](references/resolver.yaml) +
[`references/state-axis.md`](references/state-axis.md); (3) for each voice,
look up `(function × state)` in
[`references/matrix-index.yaml`](references/matrix-index.yaml) and read **only**
its `pointers:`; (4) apply the name_exposure rule for the layer.

Source-of-truth files (paths are relative to this skill's `references/` directory):
- [`references/resolver.yaml`](references/resolver.yaml) — function ↔ name ↔ visual, class (ANP/EP/Meta), tier, blends, `name_exposure`.
- [`references/matrix-index.yaml`](references/matrix-index.yaml) — `(function × state)` → 1-line essence + the exact pointers to load.
- [`references/state-axis.md`](references/state-axis.md) — the S0–S4 axis and per-layer aliases.
- [`references/bitwize-attachment.md`](references/bitwize-attachment.md) — where, inside each bitwize skill, to inject DNA.
- [`references/bitwize-provisioning.md`](references/bitwize-provisioning.md) — the bitwize config + craft-override surface, and the generator script (run before music work).
- `references/entities/`, `references/states/`, `references/cross-cutting/` — the atomic snippets the pointers resolve to. A cell's `pointers:` list is written relative to `references/` (e.g. `entities/fighter.md` → `references/entities/fighter.md`).

## Step 1 — Gate (always first)

Use `AskUserQuestion`:

> **Artist / Projekt = the Agency System?** (Music · Novel · Design)

- **No** → exit silently. Do nothing else; do not load any snippet.
- **Yes** → continue.

If the active album folder or open file already makes it unambiguous that this
is the Agency System, you may state that you've detected it and skip straight to
Step 2 — but when in doubt, ask.

## Step 2 — Determine the layer

- **Music** — albums, lyrics, Suno prompts, mastering.
- **Novel** — chapters, scenes, the Kohärenz-Protokoll.
- **Design** — cover art, image prompts, ASDLS.

Infer from the active file/album when possible; otherwise ask. The layer
decides the **name_exposure** rule (Step 5).

## Step 3 — Load the spine (once per session)

Read [`references/resolver.yaml`](references/resolver.yaml) and
[`references/state-axis.md`](references/state-axis.md). These are small and
always loaded. Do **not** bulk-read the `entities/`, `states/`, or
`cross-cutting/` directories — those are pulled per cell only.

## Step 4 — Per task, look up the cell(s)

For each voice in play:

1. If the source text uses a **name** (novel), map it to its **function** via
   `resolver.yaml → aliases`.
2. Determine the **state** (S0–S4) from the scene/track's arousal/conflict.
   `state-axis.md` defines the axis; `conflict_with` / `kernwelt_class` /
   `yellow_type` are orthogonal sub-tags.
3. Open [`references/matrix-index.yaml`](references/matrix-index.yaml) at
   `cells.<function>.<state>`. Read the `inline` essence, then `Read` **only**
   the files in `pointers` (each path is relative to `references/`).
4. Apply the layer overlay from `matrix-index.yaml → defaults.layer_overlays`
   (music = hard-rules; design = the visual cross-cutting bundle; novel = none).
5. **Blends** (e.g. the lyric "Ich" in *Lass mich*): resolve via
   `resolver.yaml → blends`, then load each member's active cell.

Token discipline: a typical lyric cell is `entities/<fn>.md` + `states/<sN>.md`
(+ `collision-matrix.md` at S2/S3). Never pre-load the whole tree.

> **Slug note:** function keys use underscores, but entity **filenames use
> hyphens** — `child_freeze` → `entities/child-freeze.md`,
> `sexualized_override` → `entities/sexualized-override.md`. Don't substitute the
> key into `<fn>.md` literally. The canonical path is the function's `entity:`
> field in `resolver.yaml`, and every `pointers:` entry in `matrix-index.yaml`
> is already the exact filename — use those.

## Step 5 — name_exposure gate (hard rule)

From `resolver.yaml → name_exposure_default`:
- **novel** → the alter NAME may appear.
- **music** and **design** → **function / role ONLY**. The personal name
  (Kael, Nyx, Selene, …) must NEVER reach a lyric, a Suno metatag, promo copy,
  cover-art prompt, or any public field. The descriptive form
  `[female belt-alto, growl, dry mid-distance mic]` is allowed; the character
  form `[The Fighter]` / "Nyx" is not. This enforces
  `overrides/voice-craft-principles.md` and `cross-cutting/hard-rules.md`.

## Step 6 — Attach to the running process

`bitwize-attachment.md` maps each bitwize skill's own phase/field to the refs to
load (e.g. lyric-writer → per-POV `entities/<fn>` + state + hard-rules;
album-art-director → the design overlay + state hex; suno-engineer →
function-form metatags, no names; release-director → no-labels compliance).
Novel writing phases pull entities **by name** + `state-axis` + `collision-matrix`.

## Provisioning bitwize (music layer, before the chain)

Before the first bitwize skill runs for the artist, make sure bitwize's own
config + craft overrides reflect this artist. Full surface + script in
[`references/bitwize-provisioning.md`](references/bitwize-provisioning.md).

- **Config** lives at `~/.bitwize-music/config.yaml` (rendered from
  `.claude/bitwize-music.config.template.yaml` by the SessionStart hook). For the
  Agency System it is usually already correct. To switch artist, render it and
  then run the bitwize `rebuild_state` MCP tool (the override path is cached).
- **Craft overrides** (`overrides/lyric-writing-guide.md`, `suno-preferences.md`,
  `mastering-presets.yaml`, `pronunciation-guide.md`, …) encode the no-labels /
  function-form rule and other craft. (Re)generate them with the script —
  **dry-run first**, since these files are curated and the script backs up
  before overwriting:

  ```bash
  python3 scripts/provision_bitwize.py overrides            # dry-run
  python3 scripts/provision_bitwize.py overrides --write    # apply (+ .bak)
  ```

- It will **never** touch album/project-specific overrides
  (`visual-language-guide.md`, `the-eleven.md`, `kohaerenz-protokoll-*`,
  `image-style-spec.md`, `genre-*`) — those hold album content, not craft.

## Optional — SessionStart nudge

A SessionStart reminder-hook may nudge: "Working on the Agency System? Invoke
the-agency-system to load DNA." The hook only reminds; this skill still gates.

## Worked examples (one per layer)

**Music — lyric-writer, *Lass mich, lass mich atmen* T07, state S3, blend
fighter + child_freeze.**
→ Gate = Yes; layer = music. Resolve the blend via `resolver.yaml → blends`,
load `entities/fighter.md` + `entities/child-freeze.md` + `states/s3.md` +
`cross-cutting/collision-matrix.md` + `cross-cutting/hard-rules.md`.
Output uses **function descriptors only — no names** (no "Nyx", no `[Fighter]`).

**Design — album-art-director, cover for a track that peaks at S3, lead =
collapsed.**
→ Gate = Yes; layer = design. Look up `cells.collapsed.S3`, load
`entities/collapsed.md` + `states/s3.md`, then the design overlay
(`color-thermodynamics`, `glitch-typology`, `semiotic-symbols`,
`composition-rules`, `specd-formula`, `hard-rules`). Build the SPECD prompt with
**role language only** — Flame/Corrupted hex, datamoshing, ≤5% state color.
The personal name never enters the prompt.

**Novel — a chapter scene where Selene mediates a clash between Nyx and Kiko at
state S2.**
→ Gate = Yes; layer = novel. Names map to functions
(`Selene→integrator`, `Nyx→fighter`, `Kiko→child_freeze`) via
`resolver.yaml → aliases`. Load `entities/integrator.md`, `entities/fighter.md`,
`entities/child-freeze.md` + `states/s2.md` + `cross-cutting/collision-matrix.md`.
Here the **names ARE allowed** — this is the only layer where they may surface.
