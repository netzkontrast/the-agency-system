# the-agency-system

Working tree for **the-agency-system** music projects — concept albums,
documentary-edge work, and multi-voice writing across electroacoustic,
dark folk, orchestral electronic, dark electro rock, industrial darkwave,
trip-hop, and ambient territory.

## What's in this repo

- **`artists/`** — Album projects, organised as
  `<artist>/albums/<genre>/<slug>/`. Each album folder holds its own
  README (concept, sequence, sonic palette, tracklist), research notes
  and sources where relevant, voice DNA reference, art direction, and
  track files (`tracks/01-...md`, etc.).
- **`overrides/`** — Cross-project preferences applied to every session:
  lyric craft, Suno V5 prompt mappings, vocal-register defaults,
  documentary source-priority standards, mastering presets per genre,
  pronunciation entries, voice-craft principles, promotion preferences.
- **`audio/`** — Mastered audio (tracked in Git LFS).
- **`documents/`** — PDFs and reference documents (tracked in Git LFS).
- **`CLAUDE.md`** — Workflow mandates and session-start guidance.

## Conventions

- **Album-specific content** (alter / character names, narrative DNA,
  per-track pronunciations, source material tied to one album) lives
  inside that album's folder — never in `overrides/`.
- **Voices in multi-voice tracks are recognised by syntax**, never by
  labels. See `overrides/voice-craft-principles.md` for the rule.
- **Documentary discipline applies** to any track referencing real
  people or events — five rules in `overrides/research-preferences.md`.
- **Git LFS required** for `audio/` and `documents/`. Run
  `git lfs install` once per machine.

## Working on an album

Inside any album folder you'll find a `README.md` with the locked
concept, sequence, and per-track table. Track files in `tracks/` hold
lyrics (both Suno-formatted and streaming-ready), Style Box, production
notes, and generation log. Research-driven albums add `RESEARCH.md` and
`SOURCES.md` at the album root.

## Plugin install

**Local development (from source)** — Spec 022 dev-install:
```bash
bash bin/agency-dev-install
```

Then load the plugin locally:
```bash
claude --plugin-dir .
```

> The dev-install script is invoked via `bash` so it works regardless
> of the file's executable bit. If you prefer the bare form, run
> `chmod +x bin/agency-dev-install` once after clone.

**From marketplace**:
```bash
/plugin install agency-system@netzkontrast
```
<!-- Spec: Plan/002-manifest-and-marketplace/spec.md -->
<!-- Spec: Plan/022-dev-mode-install/spec.md -->
