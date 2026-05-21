# Bitwize provisioning — config + craft overrides

How the skill prepares the bitwize-music environment **before** music work, so
bitwize tooling behaves correctly for the artist. Two surfaces: the **config**
(artist identity + paths) and the **craft overrides** (how skills write).

**Contents:** [1. Config](#1-config-file) · [2. Override surface](#2-override-surface)
· [3. What to generate vs leave alone](#3-what-to-generate-vs-leave-alone)
· [4. The generator script](#4-the-generator-script)
· [5. Provisioning procedure](#5-provisioning-procedure)

---

## 1. Config file

- **Path:** `~/.bitwize-music/config.yaml` (home-relative — **not** the plugin dir).
- **How it appears:** the SessionStart hook in `.claude/settings.json` runs
  `.claude/scripts/setup-bitwize-music.sh`, which renders
  `.claude/bitwize-music.config.template.yaml` → `~/.bitwize-music/config.yaml`,
  substituting `${REPO}` with the repo path. Existing configs are left untouched
  unless their `content_root` no longer matches this repo.
- **Schema (keys that matter):**
  - `artist.name` (REQUIRED — drives the `artists/<artist>/…` path segment),
    `artist.genres`, `artist.style`
  - `paths.content_root` (REQUIRED), `paths.audio_root`, `paths.documents_root`,
    `paths.overrides` (→ becomes `overrides_dir` in state), `paths.ideas_file`
  - `generation.service` (`suno`), `.require_suno_link_for_final`,
    `.max_lyric_words`, `.require_source_path_for_documentary`
  - `urls.*`, `database.*`, `cloud.*`, `promotion.*`, `sheet_music.*`
- **Switch artist:** rewrite `artist.name` + `paths.*` (or run
  `/bitwize-music:configure`), then **run `rebuild_state`**. `load_override`
  reads `state.config["overrides_dir"]` from the indexer cache, not the live
  config — so a config change is invisible until the state is rebuilt.

> The skill's `scripts/provision_bitwize.py config` renders the same template
> for a chosen artist on demand (dry-run by default).

## 2. Override surface

bitwize loads overrides through `load_override(name)` → `{overrides_dir}/{name}`.
The **craft** overrides (cross-project taste — safe to (re)generate):

| Override file | Loaded by | Real top-level sections |
|---|---|---|
| `lyric-writing-guide.md` | lyric-writer, lyric-refiner | Style Preferences · Point of View · Vocabulary (Prefer/Avoid) · Themes (Focus On/Avoid) · Structure Preferences · Custom Rules |
| `suno-preferences.md` | suno-engineer | Genre Mappings · Default Settings · Vocal Preferences · Avoid (Genres/Descriptors/Production Terms/**Artist Names**) · Instrument Preferences · Section-Tag Conventions · Inline Voice Metatag Pattern · Exclude Styles Defaults |
| `mastering-presets.yaml` | mastering-engineer | `genres:` (per-genre EQ/LUFS/comp) + `defaults:` |
| `research-preferences.md` | researchers-* | Source Priority · Verification Standards · Research Depth · Bilingual Source Use · Trusted Sources · Album-Type Workflow · Documentary Five Rules |
| `promotion-preferences.md` | promo-writer | Tone & Voice · Platform Priorities · Messaging Themes · Hashtag Preferences · AI Music Positioning · Per-Platform Style Notes · Release Cadence |
| `pronunciation-guide.md` | lyric-writer, pronunciation-specialist, lyric-reviewer, suno-engineer, session-start | Artist & Studio Names (**table**) · Cross-Project Recurring Terms · Homographs · Tech Terms · Genre Jargon · Acronyms · Non-English Names · Numbers · Auto-Fix Rules. **Validated: must contain a markdown table, ≤200KB.** |
| `voice-craft-principles.md` | (principle doc; cited in CLAUDE.md) | The Hard Rule · What Differentiates a Voice · Application Reflex · Cross-Project Implications |

## 3. What to generate vs leave alone

**Generate / overwrite (craft):** the seven files above. Their templates live in
`scripts/templates/*.tmpl` and carry the Agency-System craft — above all the
**no-labels / function-form rule** (mirrors `cross-cutting/hard-rules.md` and
`overrides/voice-craft-principles.md`): no alter personal name in any lyric,
Suno metatag, art prompt, or promo field; descriptive register only
(`[female belt-alto, growl, dry mid-distance mic]`, never `[Fighter]`).

**Never touch (album/project-specific — they hold album content, not craft):**
`visual-language-guide.md`, `image-style-spec.md`,
`kohaerenz-protokoll-sprach-dna.md`, `the-eleven.md`, and any `genre-*.md`. The
generator hard-denylists these.

## 4. The generator script

`scripts/provision_bitwize.py` (Python 3.8+; PyYAML optional, for validating the
rendered `mastering-presets.yaml`). Dry-run by default; `--write` applies and
backs up every existing target to `<file>.bak-<timestamp>`.

```bash
S=skills/theagencysystem/scripts/provision_bitwize.py
python3 $S list                              # show craft allowlist + denylist
python3 $S overrides                         # dry-run: what would change
python3 $S overrides --only suno-preferences.md --diff
python3 $S overrides --write                 # apply (backs up existing)
python3 $S config --artist-slug another-artist   # dry-run a config for a new artist
python3 $S config --artist-slug another-artist --write   # then run rebuild_state
```

## 5. Provisioning procedure

1. **New artist?** `config --artist-slug <slug> --write`, then run the bitwize
   `rebuild_state` MCP tool. (For the Agency System the SessionStart hook
   already renders the config — usually nothing to do.)
2. **Sync craft:** `overrides` (dry-run) → review → `overrides --write`. Because
   the existing files are curated, **always dry-run first** and keep the `.bak-*`
   files until the result is verified.
3. Craft-override *content* edits do **not** need `rebuild_state` (only config /
   `overrides_dir` / artist changes do).
4. Proceed into the bitwize chain; the gate skill loads the matrix DNA per task.
