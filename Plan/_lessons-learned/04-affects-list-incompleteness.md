---
lesson_id: 04
slug: affects-list-incompleteness
severity: medium
seen_in: [spec-002, spec-004-first-attempt, spec-004a-first-attempt]
applies_to:
  - spec-template
  - spec-author
captured_at: 2026-05-17
---

# Spec `affects:` lists keep being incomplete

## Pattern (3 instances)

- **Spec 002**: `Files: Create:` listed `tests/smoke/test_manifest.py`, but the YAML `affects:` did not. Jules created the file as instructed, technically violating anti-pattern #6 (file outside `affects:`).
- **Spec 004 first attempt**: `affects:` listed 16 handler files but the implementation legitimately needed `_atomic.py`, `_shared.py`, `processing/_album_stages.py`, `processing/_helpers.py` as decomposition helpers. These weren't in `affects:`, surfacing as drift.
- **Spec 004a first attempt**: `affects:` enumerated 5 of 10 vendor subdirectories under `tools/`. The other 5 (`database`, `mixing`, `n8n`, `promotion`, `userscripts`) were silently excluded, and a cross-subtree import (`mastering/master_tracks` → `mixing/mix_tracks`) made the partial port unbuildable.

In every case, Jules behaved correctly per the spec's letter, but the spec was wrong.

## What to change

### Spec template should require frontmatter ≥ Files: union

Add a pre-merge spec-author check (probably a script under `Plan/_lint/check_affects.py`):
- Parse every spec's frontmatter `affects:` list.
- Parse the spec's `## Files` section (Create / Modify / Delete bullets).
- For every path under `## Files`, assert it appears in `affects:`.
- Fail the lint if any path is missing.

### Vendor-port specs should use directory-wildcard `affects:`

For "port the whole subtree" specs (like 004a), the `affects:` entry should be a single directory path with a comment:

```yaml
affects:
  - servers/agency-mcp/src/agency_mcp/tools/   # ENTIRE SUBTREE — every .py under bitwize-music v0.91.0 tools/.
```

NOT 10 enumerated subdirs. The directory pattern is the contract; the Done-When test should be a directory-diff check against the source.

### Spec template should call out helper-file allowance

If a spec ports vendor code, the Approach should explicitly allow decomposition helpers (`_shared.py`, `_atomic.py`, `_helpers.py`) and require them to be enumerated in `affects:` once the decomposition is decided. Don't leave Jules guessing.

## Concrete deliverable for the meta-spec

Add a lint script `Plan/_lint/check_affects.py`. Update spec template to call out the directory-wildcard pattern for vendor ports. Update JULES_PROTOCOL.md §5 anti-pattern #6 to clarify that drift includes "file is in Files: but not in affects:" — the spec is wrong, not Jules.
