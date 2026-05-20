---
slug: vision-domain-isomorphism
type: spec
status: vision
owner: claude
created: 2026-05-20
updated: 2026-05-20
summary: Path B — the full domain isomorphism endgame. A unified per-domain registry (Domain base class with register_handlers/register_skills/register_phases/register_gates/register_schemas), one target tree layout, one migration strategy. Path A levers (vision/specs/10-harness-ladder.md §11) are the active incremental path; this spec is the long-horizon target.
depends_on:
  - vision/specs/10-harness-ladder.md
  - vision/specs/12-vocabulary.md
referenced_by:
  - vision/specs/10-harness-ladder.md
supersedes:
  - Plan/harness/restructure/spec.md
---

## §1 Motivation

`Plan/harness/design.md` §11.4 names Path B — the structural restructure that lifts uniformity from 6/10 (today) to 10/10 (native) by making **every domain conform to the same five-file, single-base-class interface**. The current codebase has three registration patterns, two tag conventions, manifest gaps on the novel domain (56 handlers absent from `manifest.json`), and a skills tree that's top-level for music/jules/agentic but nonexistent for novel/context/shared. Path A (the chosen first-implementation path) papers these over with harness-side normalisation; Path B cures them at the source.

The case for doing Path B *eventually*:

1. **Every harness branch / fallback disappears.** `tests/_harness/normalisation.py` exists only because the source isn't uniform. Under Path B, `list_tools(domain="novel")` reads cleanly through `NovelDomain.list_tools()` — no manifest fallback, no tag-conversion logic, no "Pattern A vs B vs C" worry.
2. **Phase 7 onward becomes trivial.** Adding a handler module under `domains/music/handlers/X.py` automatically gets the right tag, the right name format, the right manifest entry, and the right test fixtures. The author writes one decorator call.
3. **External-agent reachability (L3) gains documentation symmetry.** A first-touch agent reading `agency --bootstrap` sees five identically-shaped domains. No "music has skills but context doesn't" surprise.
4. **The "phantom domain" class of bug becomes impossible.** A domain that exists in code but not in manifest is a category error under Path B — the `Domain` base class controls both.

The case for **not** rushing it:

- 2-3 weeks of refactor work; conflicts with every concurrent Phase 2-8 PR that touches `handlers/`.
- Phase 7 specs (015 novel skills catalogue, 016 agentic handlers, 018 overrides migration, 021 novel prompt-builders) all assume the current `handlers/<domain>/` layout. Starting Path B mid-Phase-7 forces re-pointing those dispatches.
- The 9/10 score that Path A delivers is sufficient for the harness's intended consumers (Phase 1 smoke tests, in-session dogfooding, external-agent CLI access).

This spec exists to make Path B's design visible and reviewable *before* it's scheduled, so when the orchestrator does schedule it the decisions are pre-baked.

State plainly: this spec is `status: vision`, not `status: ready`. The active path stays Path A.

## §2 Target tree

```
servers/agency-mcp/src/agency_mcp/
└── domains/
    ├── _base/
    │   ├── __init__.py
    │   ├── domain.py          # class Domain — name, state_cls, handler_modules, tool_only,
    │   │                      #                 register(mcp), warm(), list_skills()
    │   ├── state.py           # class DomainState — base cache abstraction; warm() / invalidate()
    │   ├── handlers.py        # @tool(domain="X", requires_state=[...]) decorator
    │   ├── manifest.py        # sync_manifest_from_registrations(mcp) — boot-time regeneration
    │   └── conventions.py     # invariants (per Plan/harness/VOCABULARY.md):
    │                          #   - DOMAIN_RE = r'^[a-z]+$'
    │                          #   - TOOL_NAME_RE = r'^[a-z]+_[a-z_]+$'  (<domain>_<verb>)
    │                          #   - TAG_FMT = "domain:{name}"
    │                          #   - SKILL_SCHEMA = required keys per VOCABULARY §6A
    │                          #     + skill_kind enum per VOCABULARY §4.2
    │                          #     (domain | tool | orchestrator | meta | discipline |
    │                          #      workflow | persona | analysis | agent-template)
    │                          #   - SUMMARY_CAP_SKILLS = 120   # per VOCABULARY §6A
    │                          #   - SUMMARY_CAP_SPECS = 240    # per VOCABULARY §6A
    │                          #   - CONTENT_TIER_T1_CAP = 200  # chars (VOCABULARY §6D)
    │                          #   - CONTENT_TIER_T2_CAP = 5120 # bytes (VOCABULARY §6D)
    │                          #   - RECIPROCITY = { supersedes → superseded_by, ... }
    │                          #     (VOCABULARY §6B reciprocity rules)
    │                          #   - REPAIR_TIER_RE = r'^T[1-4]$' (VOCABULARY §6C)
    │                          #   - BinaryEnvelope = TypedDict[type, path, size_bytes, mime_type, sha256]
    │                          #   - ADR_FM_SCHEMA = MADR 4.0.0 per Plan/decisions/readme.md
    │
    ├── music/
    │   ├── __init__.py        # class MusicDomain(Domain):
    │   │                      #     name = "music"
    │   │                      #     state_cls = MusicState
    │   │                      #     handler_modules = [core, audio, content, ideas, ...]
    │   ├── handlers/          # 17 modules; each exports `register_to(mcp, *, domain, state)`
    │   ├── state.py           # class MusicState(DomainState) — wraps existing StateCache for now
    │   ├── skills/            # 54 skills moved here from skills/music/
    │   └── tests/             # moved from tests/unit/music/
    │
    ├── novel/    # 13 handler modules — see _migration/checklist.md for module-by-module map
    ├── jules/    # 6 handler modules + 1 skill
    ├── context/  # 2 handler modules; tool_only = False (anchor tools surface here)
    └── shared/   # 6 handler modules; tool_only = True (no skills expected)
```

The `agentic` skill-only domain (today at `skills/agentic/`) doesn't get a `domains/agentic/` because it has no handlers. Open question for the migration: either move `agentic/` skills to `shared/skills/agentic/` (cross-cutting) or keep them at the repo root as `skills/agentic/` (preserves the "cross-domain skill" semantics). Recommendation: keep them at the repo root with a `_root_skills_only = True` carve-out documented in `conventions.py`.

## §3 Domain base class

contract (full signature)

```python
# servers/agency-mcp/src/agency_mcp/domains/_base/domain.py

from abc import ABC
from pathlib import Path
from typing import ClassVar
from fastmcp import FastMCP
from .state import DomainState
from .manifest import register_for_manifest

class Domain(ABC):
    """The shape every domain conforms to.

    Subclasses declare class-level metadata and a list of handler modules.
    The base class handles registration, manifest sync, skill discovery, and warming.
    """

    name: ClassVar[str]
    """Lowercase identifier. Matches DOMAIN_RE."""

    state_cls: ClassVar[type[DomainState]]
    """The DomainState subclass that owns this domain's cache."""

    handler_modules: ClassVar[list]
    """Ordered list of modules, each exporting `register_to(mcp, *, domain, state)`."""

    tool_only: ClassVar[bool] = False
    """True means this domain has no `skills/` directory (formal opt-out from L-η)."""

    skill_root: ClassVar[Path | None] = None
    """Override to relocate skill discovery (e.g. cross-cutting `agentic/`).
       Default: `<package>/<self.name>/skills/`."""

    # --- lifecycle ---

    def __init__(self):
        self.state = self.state_cls()

    def register(self, mcp: FastMCP) -> None:
        """Register every handler module with the given MCP instance.

        Each module's `register_to(mcp, *, domain=self.name, state=self.state)`
        is called in declaration order. After all modules register,
        register_for_manifest() records the domain's eager/deferred tool
        classification in the codemode manifest."""
        for module in self.handler_modules:
            module.register_to(mcp, domain=self.name, state=self.state)
        register_for_manifest(mcp, domain=self.name)

    def warm(self) -> None:
        """Warm the domain's cache. Called by harness_warm() and by tools
        decorated with `requires_state=[...]` (lever L-ε)."""
        self.state.warm()

    # --- introspection ---

    def list_skills(self) -> list[dict]:
        """Walk this domain's skills/ directory, parse each SKILL.md
        frontmatter against conventions.SKILL_SCHEMA, and return
        list of {name, path, frontmatter, body}.

        Fails boot loudly if any SKILL.md violates the required-base
        schema (lever L-δ enforced at the source)."""
        if self.tool_only:
            return []
        root = self.skill_root or (Path(__file__).parent.parent / self.name / "skills")
        return _parse_skill_tree(root)

    def health(self) -> dict:
        """Return {name, tool_count, skill_count, state_warm}.
        Drives `agency --bootstrap` and L1's harness diagnostics."""
        return {
            "name": self.name,
            "tool_count": self.state._registered_tool_count,
            "skill_count": len(self.list_skills()),
            "state_warm": self.state.is_warm(),
        }
```

The `@tool` decorator in `_base/handlers.py`:

```python
# servers/agency-mcp/src/agency_mcp/domains/_base/handlers.py

from typing import Callable
from fastmcp import FastMCP
from .conventions import TAG_FMT, TOOL_NAME_RE

def tool(
    mcp: FastMCP,
    *,
    domain: str,
    requires_state: list[str] | None = None,
    hidden: bool = True,
    defer_schema: bool = True,
    **mcp_kwargs,
) -> Callable:
    """Canonical decorator. Used by every handler module across every domain.

    Enforces:
    - tags includes `domain:<name>` (TAG_FMT).
    - function name matches TOOL_NAME_RE = `^<domain>_<verb>$`.
    - If `requires_state` is set, wraps the handler so the listed
      cache-warming tools are auto-invoked first (lever L-ε).
    """
    def wrap(fn: Callable) -> Callable:
        if not TOOL_NAME_RE.match(fn.__name__):
            raise ValueError(
                f"Tool {fn.__name__} does not match {TOOL_NAME_RE.pattern}; "
                f"per domain '{domain}', name must be `{domain}_<verb>`."
            )
        tags = (mcp_kwargs.pop("tags", set()) or set()) | {TAG_FMT.format(name=domain)}
        if requires_state:
            fn = _wrap_with_warming(fn, requires_state)
        return mcp.tool(tags=tags, hidden=hidden, **mcp_kwargs)(fn)
    return wrap
```

## §4 Migration strategy

The restructure ships as **one PR per domain plus one base-class PR plus one server-collapse PR plus one cleanup PR — eight PRs total.** Each domain PR is parallel-safe; the others sequence.

```
PR 1 (base):          Plan/harness/restructure/_migration/01-base-class.md
                      Authors _base/ (5 files). No domain changes yet.

PR 2-6 (domains):     Plan/harness/restructure/_migration/02-music.md
                      Plan/harness/restructure/_migration/03-novel.md
                      Plan/harness/restructure/_migration/04-jules.md
                      Plan/harness/restructure/_migration/05-context.md
                      Plan/harness/restructure/_migration/06-shared.md
                      Each ports its domain into domains/<name>/. Adds
                      backward-compat shim at handlers/<domain>/__init__.py
                      that re-exports from the new location.

PR 7 (server):        Plan/harness/restructure/_migration/07-server.md
                      Collapses create_mcp() to the five-line loop.
                      Removes backward-compat shims. Deletes
                      tests/_harness/normalisation.py.

PR 8 (cleanup):       Plan/harness/restructure/_migration/08-cleanup.md
                      Updates Plan/000-overview.md §7 target tree;
                      bin/agency-dev-install line 53; docs/architecture/
                      domains.md authored.
```

Backward-compat strategy during PRs 2-6:

```python
# servers/agency-mcp/src/agency_mcp/handlers/music/__init__.py  (transitional shim)
"""Backward-compat shim during the restructure migration.

After PR 7, this file is deleted and any remaining imports from
agency_mcp.handlers.music must move to agency_mcp.domains.music.handlers."""
from ..._compat import deprecation_warning
deprecation_warning(__name__, replacement="agency_mcp.domains.music.handlers")
from agency_mcp.domains.music.handlers import *  # noqa
```

This keeps existing tests + handlers running while individual domain PRs land. The shims are deleted in PR 7.

## §5 Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Concurrent Phase 2-8 PRs conflict with PR 2-6 | High if scheduled mid-phase | Schedule after Phase 7 if Phase 7 is in flight; otherwise before |
| ~50 test files need import-path updates; manual rebase | High | PR 2-6 each include automated `sed` migration as part of the PR; mass-edit is mechanical |
| `manifest.json` runtime regeneration vs check-in version conflict | Medium | PR 1's `_sync_manifest` adds a header `"_meta": {"generated_by": "_base.manifest", "do_not_hand_edit": true}` to the generated section |
| Performance regression from `Domain.register()` abstraction overhead | Low | Boot-budget regression test in PR 1 asserts `tools/list` payload ±5%; fail loud on regression |
| Backward-compat shims linger after PR 7 | Medium | PR 7's checklist includes `grep -rln 'agency_mcp.handlers' --exclude-dir=domains` returning zero hits |
| The `Domain` abstraction proves wrong for a future domain (e.g. cross-cutting concern) | Low | `skill_root` override + `tool_only` flag already handle the two known divergences (agentic, shared); extension via additional class variables |

## §6 Compatibility with Path A

Path A is forward-compatible with Path B; the levers (L-α/β/γ) are stepping stones, not detours. See `vision/specs/10-harness-ladder.md` §11.
