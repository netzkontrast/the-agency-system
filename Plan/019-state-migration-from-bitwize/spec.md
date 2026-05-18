---
spec_id: 019
slug: state-migration-from-bitwize
status: done
owner: jules
depends_on: [003]
affects:
  - state/migrators/__init__.py
  - state/migrators/bitwize_v091_to_agency.py
  - state/migrators/_hashing.py
  - state/migrators/_atomic.py
  - migrations/agency/1.0.0.md
  - tests/integration/__init__.py
  - tests/integration/test_migration.py
  - tests/fixtures/migration/bitwize_state.json
  - tests/fixtures/migration/bitwize_config.yaml
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

# Spec 019 — State Migration From bitwize-music

## Why

Existing bitwize-music users have lived state under `~/.bitwize-music/` —
specifically `~/.bitwize-music/cache/state.json` (artist/album/track index) and
`~/.bitwize-music/config.yaml` (user-edited preferences derived from the
bitwize template). When they install the unified plugin and reach for
`/agency-system:music-resume`, that state must already be present at
`~/.agency-system/cache/state.json:music` and `~/.agency-system/config.yaml`
— otherwise their projects vanish from the resume / dashboard skills and
the user perceives the unified plugin as data-lossy.

The migration must be:

1. **Idempotent** — re-running yields no change (verified by input-hash comparison).
2. **Atomic** — partial-write under crash leaves either the old state intact OR the new state fully written, never a torn file.
3. **Reversible** — a backup snapshot of the bitwize files is preserved before any mutation, so the user can recover even if the new state is later corrupted.
4. **Dry-run-first** — the default invocation reports what would happen without writing anything.
5. **Loud-failure** — if the bitwize state schema is unexpected, the migrator refuses to write and emits a structured error, rather than fabricating defaults.

Spec 018 produced the *template* that the unified config is migrated *to*;
this spec produces the migrator script and the migration runbook.

## Done When

- [ ] `python state/migrators/bitwize_v091_to_agency.py --dry-run` exits 0 and prints a JSON line `{"would_migrate": <int>, "would_skip": <int>, "input_hash": "<sha256>"}` to stdout when both bitwize files exist; exits 0 with `{"would_migrate": 0, "would_skip": 0, "input_hash": null, "reason": "no bitwize state found"}` when neither exists.
- [ ] `python state/migrators/bitwize_v091_to_agency.py` (no `--dry-run`) writes `~/.agency-system/cache/state.json` and `~/.agency-system/config.yaml` via tempfile + `os.fsync` + atomic rename (`os.replace`), and writes a backup snapshot to `~/.agency-system/backup/<UTC-ISO-timestamp>/{bitwize-state.json,bitwize-config.yaml}` BEFORE any rename.
- [ ] After a successful migration, `~/.agency-system/cache/state.json` validates against the state.schema.json shape from spec 003 with `music.*` populated from the bitwize input and `novel`, `jules`, `agentic` populated as empty namespaced subtrees (`{}`).
- [ ] Re-running the migrator (no flags) is a **no-op**: detected by hashing the bitwize input files and comparing against `~/.agency-system/cache/state.json:_migration.input_hash`. Exit 0 with stdout `{"reason": "already migrated", "input_hash": "<sha256>"}`.
- [ ] On any non-recoverable error (schema mismatch, disk full, lock contention), the migrator exits non-zero, leaves the destination files unchanged, and emits a single-line structured JSON error on stderr `{"error": "<kind>", "msg": "<detail>"}`.
- [ ] `~/.bitwize-music/DEPRECATED.md` is written on successful migration, naming the timestamp, the destination paths, and the backup directory.
- [ ] `migrations/agency/1.0.0.md` exists and reads as a human runbook: pre-flight checks, dry-run command, real-run command, rollback instructions.
- [ ] `pytest -x tests/integration/test_migration.py` exits 0, covering: dry-run safety, atomicity (tempfile crash simulation), idempotency (second run no-op), backup creation, deprecation marker, schema mismatch path.

## Source clones (run first)

```bash
git clone --depth=1 --branch=v0.91.0 \
  https://github.com/bitwize-music-studio/claude-ai-music-skills.git \
  ~/work/vendor/bitwize-music
```

Read `~/work/vendor/bitwize-music/servers/bitwize-music-server/state/cache.py`
and any `state.schema.json` shipped there to lock down the
`~/.bitwize-music/cache/state.json` shape. If the source defines no schema,
infer from a freshly-initialised bitwize state and document the inferred
shape in `migrations/agency/1.0.0.md`.

## Files

- **Create**:
  - `state/migrators/__init__.py` — empty package init.
  - `state/migrators/bitwize_v091_to_agency.py` — the migrator CLI (argparse: `--dry-run`, `--source-dir`, `--dest-dir`, `--no-backup` flag for tests only).
  - `state/migrators/_hashing.py` — `sha256_of_files(paths: list[Path]) -> str` deterministic over sorted contents.
  - `state/migrators/_atomic.py` — `atomic_write_json(path, payload)` using tempfile + `os.fsync` + `os.replace` per POSIX atomicity rules.
  - `migrations/agency/1.0.0.md` — human-readable runbook.
  - `tests/integration/__init__.py`.
  - `tests/integration/test_migration.py` — full coverage matrix.
  - `tests/fixtures/migration/bitwize_state.json` — a 3-artist sample bitwize state file.
  - `tests/fixtures/migration/bitwize_config.yaml` — a sample bitwize config file with non-default values.
- **Modify**: none. The migrator is a standalone CLI; it does not touch handler code.
- **Move / Delete**: none in the repo; the migrator at runtime writes one file (`DEPRECATED.md`) into `~/.bitwize-music/`, which is outside the repo entirely.

## Approach

1. **Gate 1 — Confidence.** Read `Plan/000-overview.md` §1 (state on disk layout — `~/.agency-system/cache/state.json` with `{music, novel, jules, agentic, _version}` namespaces). Read spec 003's `state.schema.json` to lock the unified shape. Read the bitwize state.json shape from the vendor source. Confirm Python ≥3.11 (for `os.fsync` semantics and `tomllib`). Cite the bitwize state shape source path + the unified schema path in the PR `## Confidence` table.
2. **Clone bitwize.** Run the clone command. Generate a fresh bitwize state by running `bitwize-music` if installable in the sandbox; otherwise infer the shape from the cache module. Either way, capture the canonical shape as `tests/fixtures/migration/bitwize_state.json` (synthetic — three artists, two albums each, four tracks per album, mixed statuses).
3. **Author `_hashing.py`.** `sha256_of_files(paths)` MUST sort the input list, then hash each file's bytes concatenated with the file's relative basename — so adding / removing a file changes the hash, and reordering paths does not.
4. **Author `_atomic.py`.** `atomic_write_json(path: Path, payload: dict) -> None`:
   - Create parent dirs (`mkdir(parents=True, exist_ok=True)`).
   - Open `tempfile.NamedTemporaryFile(dir=path.parent, delete=False, suffix='.tmp')`.
   - Write `json.dumps(payload, indent=2, sort_keys=True)`.
   - `f.flush(); os.fsync(f.fileno())`.
   - `os.replace(tmp_path, path)` — POSIX-atomic.
   - Exception path: remove the tempfile, re-raise.
5. **Author the migrator.** CLI shape: `python bitwize_v091_to_agency.py [--dry-run] [--source-dir ~/.bitwize-music] [--dest-dir ~/.agency-system] [--no-backup]`.
   - Resolve source paths: `<source-dir>/cache/state.json`, `<source-dir>/config.yaml`.
   - If neither exists → exit 0, stdout `{"would_migrate": 0, "would_skip": 0, "input_hash": null, "reason": "no bitwize state found"}`.
   - Hash the source files into `input_hash` via `_hashing.sha256_of_files`.
   - Read existing `<dest-dir>/cache/state.json` if any; check for `_migration.input_hash`; if equal → exit 0 no-op, stdout `{"reason": "already migrated", "input_hash": ...}`.
   - Compose the unified payload: `{music: <bitwize_state>, novel: {}, jules: {}, agentic: {}, _version: "1.0.0", _migration: {input_hash, from: "bitwize-music v0.91.0", at: "<UTC ISO>"}}`.
   - Compose unified config: per spec 018's `references/config-diff.md` §3.1, fold the bitwize config under the `music:` key; seed `novel`, `jules`, `agentic`, `shared` from `config/agency-system.config.template.yaml`.
   - If `--dry-run`: print the JSON summary and exit 0 — write nothing.
   - Else: create backup dir `<dest-dir>/backup/<UTC-ISO>/`; copy the two source files in via `shutil.copy2`; `atomic_write_json` the new state; write the new config via the same pattern (rendered with `yaml.safe_dump`); write `<source-dir>/DEPRECATED.md` last (so a crash before that line leaves the migrator re-runnable as a no-op).
   - Schema mismatch (e.g. bitwize state top-level is not a dict) → exit 2, stderr `{"error": "schema", "msg": "..."}`.
6. **Author the runbook (`migrations/agency/1.0.0.md`).** Headings: `## Pre-flight`, `## Dry run`, `## Real run`, `## What gets written`, `## Backup and rollback`, `## Idempotency`, `## Troubleshooting`. Copy/paste-ready commands; cite this spec ID at the top.
7. **TDD — Gate 2.** RED: write the test matrix in `tests/integration/test_migration.py` using `tmp_path` and explicit `--source-dir`/`--dest-dir` overrides:
   - `test_dry_run_writes_nothing` — dry-run leaves dest empty.
   - `test_real_run_migrates_payload` — three artists land under `state.json:music.artists` exactly.
   - `test_backup_snapshot_created` — `<dest>/backup/<ts>/bitwize-state.json` exists with matching bytes.
   - `test_atomic_rename_no_torn_file` — monkeypatch `os.replace` to raise, assert dest file unchanged.
   - `test_idempotency_second_run_noop` — run twice, second exits with `reason: already migrated`.
   - `test_deprecation_marker_written` — `<source>/DEPRECATED.md` exists after success.
   - `test_schema_mismatch_exits_nonzero` — fixture with `state.json` containing a top-level list → exit 2, stderr JSON has `error: "schema"`.
   - `test_no_bitwize_state_returns_clean` — empty source dir → exit 0 with `reason: "no bitwize state found"`.
   Watch them fail. GREEN: implement the migrator. REFACTOR: extract any duplicated path-resolution into a `_paths.py` helper ONLY if it stays within `state/migrators/` (don't escape `affects:`).
8. **Gate 3 — Evidence.** Paste in PR body: `pytest -x tests/integration/test_migration.py` last 20 lines, a transcript of `python state/migrators/bitwize_v091_to_agency.py --dry-run --source-dir tests/fixtures/migration --dest-dir /tmp/agency-dest` showing the JSON summary, a transcript of the real run printing `artefacts_written`, `ls -la /tmp/agency-dest/backup/<ts>/` showing the two backup files, and a second-run transcript showing `{"reason": "already migrated"}`.
9. **Gate 4 — Self-Review.** Answer the three questions. Specifically flag any bitwize state field that did not translate cleanly to the unified shape (with rationale), and the assumption you made if the bitwize source shipped no formal `state.schema.json`.

## Acceptance (Gherkin)

```gherkin
# anchor: 019.1
Scenario: Real migration is atomic, backed-up, and idempotent
  Given ~/.bitwize-music/cache/state.json exists with 3 artists
  And ~/.bitwize-music/config.yaml exists with non-default values
  When the operator runs `python state/migrators/bitwize_v091_to_agency.py`
  Then exit code is 0
  And ~/.agency-system/cache/state.json:music.artists contains exactly 3 artists
  And ~/.agency-system/backup/<timestamp>/bitwize-state.json exists with bytes identical to the source
  And ~/.bitwize-music/DEPRECATED.md exists
  When the operator runs the same command again
  Then exit code is 0
  And stdout contains the substring "already migrated"
  And no new backup directory is created
  And the destination state.json is byte-identical to the first run

# anchor: 019.2
Scenario: Dry-run reports counts without writing any file
  Given ~/.bitwize-music/cache/state.json exists with 3 artists
  And ~/.agency-system/cache/state.json does NOT exist
  When the operator runs `python state/migrators/bitwize_v091_to_agency.py --dry-run`
  Then exit code is 0
  And stdout contains a JSON line with `would_migrate` > 0 and `input_hash` non-null
  And ~/.agency-system/cache/state.json does NOT exist
  And ~/.agency-system/backup/ does NOT exist

# anchor: 019.3
Scenario: Schema mismatch refuses to write and reports the error
  Given a synthetic bitwize state.json whose top-level is a JSON list, not an object
  When the operator runs the migrator without --dry-run
  Then exit code is 2
  And stderr contains a JSON object with `error` equal to "schema"
  And no file under ~/.agency-system/ is created or modified

# anchor: 019.4
Scenario: Crash during atomic rename leaves the destination unchanged
  Given an existing destination state.json with a previous migration
  And the test harness monkeypatches os.replace to raise OSError mid-call
  When the operator runs the migrator
  Then the destination state.json is byte-identical to its pre-call contents
  And no torn temporary file remains in the destination directory
```

## Out of scope

- Migrating any per-album files under `artists/`, `audio/`, `documents/` — those live in the repo, not under `~/.bitwize-music/`, and require no migration.
- Migrating bitwize plugin install / uninstall — covered by spec 020.
- Rolling forward to `_version: "1.1.0"` and beyond — this migrator is `bitwize_v091 → agency_v1.0.0` only; future migrators are new files under `state/migrators/`.
- Translating bitwize override files — overrides were ported in spec 005, no user-state migration needed.
- A GUI / TUI for migration — CLI only.
- Migrating Claude Code session history or message logs.

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4)
- `Plan/000-overview.md` §1 (unified state-on-disk layout — `~/.agency-system/cache/state.json` namespaced top-level keys + `_version: "1.0.0"`)
- `Plan/SOURCES.md` (bitwize-music v0.91.0 clone command)
- Spec dependency: `Plan/003-unified-statecache-port/spec.md` (`state.schema.json` shape the migrator writes against)
- Spec dependency: `Plan/018-overrides-and-config-migration/spec.md` (config template + `references/config-diff.md` migration table)
- Backward link: `Plan/017-hooks-port-and-extend/spec.md` (`check_version_sync.py` detects the drift this migrator resolves)
- Forward link: `Plan/020-bitwize-deprecation-and-docs/spec.md` (final cutover after successful migration)
- POSIX atomic-rename reference: `os.replace` semantics — https://docs.python.org/3/library/os.html#os.replace
- Vendor source (read-only): `~/work/vendor/bitwize-music/servers/bitwize-music-server/state/cache.py`
