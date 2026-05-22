---
lesson_id: 03
slug: evidence-with-polluted-pythonpath-masks-broken-imports
severity: high
seen_in: [spec-004-first-attempt]
applies_to:
  - jules-protocol
  - spec-template
  - review-subagent
captured_at: 2026-05-17
---

# Evidence captured under polluted PYTHONPATH masks broken imports

## Pattern

Spec 004 first attempt (PR #36) shipped a 15k-line PR where the production code physically did not import. `core.py` had `from tools.state.indexer import write_state`; `tools/` didn't exist on the branch. Jules' Evidence block showed:

```bash
$ PYTHONPATH=$PWD/src:$HOME/work/vendor/bitwize-music uv run pytest -x ...
4 passed
```

The tests passed only because `~/work/vendor/bitwize-music` was prepended to `PYTHONPATH`, making bitwize's source act as a substitute for the non-existent `agency_mcp.tools.*` packages. Without that PYTHONPATH addition, `python -c "from agency_mcp.server import create_mcp; create_mcp()"` raised `ModuleNotFoundError`.

This is **evidence theatre**: the artefact was produced, but in an environment that doesn't represent what a clean install would do. Gate 3's purpose is broken.

## What to change

### JULES_PROTOCOL Gate 3 should require "clean-install verification":

> **Evidence MUST be captured under a clean install.** No `PYTHONPATH` additions that point outside the repo (e.g. to `~/work/vendor/*`). No `pip install -e` of unrelated source. The Evidence block should show the exact `python -m pytest` / `python -c` invocation, and any `PYTHONPATH=` prefix must point ONLY to paths inside the repo.

Specifically forbid:
- `PYTHONPATH=...vendor...` — bleeds vendor into resolution.
- `cd ~/work/vendor/<repo> && pytest` — wrong cwd, wrong sys.path.
- `pip install -e ~/work/vendor/<repo>` — same.

### Spec template should add a Done-When for clean-install:

> - [ ] `python -c "from <package>.<entry> import <symbol>"` exits 0 from a clean install (no vendor on `PYTHONPATH`). Paste the exact invocation + exit code in Evidence.

### Review subagent template should always include:

> Verify Evidence was captured under a clean install. Specifically check the `PYTHONPATH=` prefix of every pytest/python invocation in the PR body. If any points outside the repo (e.g. to `~/work/vendor/`), flag as a Gate-3 violation regardless of test-pass status.

## Concrete deliverable for the meta-spec

Patch JULES_PROTOCOL.md Gate 3 + add clean-install Done-When to the spec template + bake the check into the review-subagent dispatch template.
