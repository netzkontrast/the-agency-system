# Config diff — bitwize-music.config.template.yaml → agency-system.config.template.yaml

> Embedded into `Plan/018-overrides-and-config-migration/`. Authored by spec
> 018 itself; this file is the auditable record of *what changed* when bitwize's
> template was unified into the agency-system template. Future config bumps
> must extend this diff (append, not overwrite).

## 1. Scope

The bitwize plugin shipped exactly one user-facing config template at
`vendor/bitwize-music/config/bitwize-music.config.template.yaml`. Under the
unified plugin, all user config lives in **one** file at
`~/.agency-system/config.yaml`, seeded from
`config/agency-system.config.template.yaml`. The shape is namespaced top-level
so each domain owns its own subtree without colliding.

## 2. Top-level shape

```yaml
# agency-system.config.template.yaml
version: "1.0.0"
music: { ... }       # 100% superset of bitwize-music.config.template.yaml
novel: { ... }       # NEW — novel-side defaults
jules: { ... }       # NEW — Jules orchestration defaults
agentic: { ... }     # NEW — agentic surface defaults
shared: { ... }      # NEW — cross-domain (logging, telemetry-off, cache locations)
```

## 3. Diff matrix (preserved keys, renamed keys, new keys)

### 3.1 Preserved verbatim under `music:` (no behaviour change)

Every key under bitwize's template moves under `music:` with no rename:

- `music.artist_name` (was `artist_name`)
- `music.default_genre` (was `default_genre`)
- `music.audio_root` (was `audio_root`)
- `music.suno.*` (was `suno.*`)
- `music.mastering.preset` (was `mastering.preset`)
- `music.lyrics.style_box_strict` (was `lyrics.style_box_strict`)
- `music.research.priority_sources` (was `research.priority_sources`)
- `music.promo.tweet_template` (was `promo.tweet_template`)
- `music.release.distributor_metadata_path` (was `release.distributor_metadata_path`)

Spec 019 (state migration) hashes the bitwize file and uses this table to
emit the music-namespaced equivalent without data loss.

### 3.2 New under `novel:`

- `novel.author_name` — default author when creating a new work.
- `novel.default_genre` — default genre subfolder under `novels/<author>/works/<genre>/<slug>/`.
- `novel.dramatica_defaults_path` — points at `overrides/dramatica-defaults.md`.
- `novel.ncp_defaults_path` — points at `overrides/ncp-defaults.md`.
- `novel.prose_style_guide_path` — points at `overrides/prose-style-guide.md`.
- `novel.narrative_preferences_path` — points at `overrides/narrative-preferences.md`.
- `novel.gates.block_on_dramatica_decidable` — `true` by default; if `false`, gate findings become warnings.

### 3.3 New under `jules:`

- `jules.branch_default` — `claude/agency-plugin-refactor-PgMQ4` per the working branch.
- `jules.pr_base` — `Master` (capitalised — bitwize convention preserved).
- `jules.confidence_threshold` — `0.90` (Gate 1 of JULES_PROTOCOL).

### 3.4 New under `agentic:`

- `agentic.specs_dir` — `~/.agency-system/agentic/specs/`.
- `agentic.plans_dir` — `~/.agency-system/agentic/plans/`.
- `agentic.workflows_dir` — `~/.agency-system/agentic/workflows/`.
- `agentic.research_dir` — `~/.agency-system/agentic/research/`.
- `agentic.ralph_dir` — `~/.agency-system/agentic/ralph/`.
- `agentic.cache_db_path` — `~/.agency-system/agentic/cache/index.db`.

### 3.5 New under `shared:`

- `shared.log_level` — `INFO`.
- `shared.telemetry_enabled` — `false` (opt-in only).
- `shared.state_cache_path` — `~/.agency-system/cache/state.json`.
- `shared.backup_dir` — `~/.agency-system/backup/`.

### 3.6 Removed / deprecated

- No bitwize keys are removed — every one is preserved under `music:` for
  zero-loss migration. If any prove obsolete at 1.1.0, deprecate via a
  `WARN` log on load and remove no earlier than 2.0.0.

## 4. Migration touch-points

- Spec 019 reads the bitwize template + the user's
  `~/.bitwize-music/config.yaml` and renders the namespaced unified config.
- The override paths added in §3.2 must exist before the template is
  considered valid — spec 018 ships placeholder files so the references
  resolve immediately, and downstream spec 020 documents user customisation.

## 5. Verification command

```bash
# Lists every bitwize key and confirms each maps to a music.* equivalent.
python3 -c "import yaml,sys; \
  b=yaml.safe_load(open('~/work/vendor/bitwize-music/config/bitwize-music.config.template.yaml')); \
  u=yaml.safe_load(open('config/agency-system.config.template.yaml')); \
  missing=[k for k in b if k not in u.get('music',{})]; \
  sys.exit(0 if not missing else (print('MISSING:',missing) or 1))"
```

The verification command above is the artefact pasted into spec 018's PR
`## Evidence` block; if it exits non-zero, the unified template lost a
bitwize key and must be amended before merge.
