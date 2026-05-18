---
slug: harness-restructure-domains
status: vision
owner: claude
depends_on: [harness/design]
related: [023, 022, 008, 015, 016, 018, 021]
phase: 7+   # gates Phase 7 (specs 015/016/018/021); should not start until Phase 7 batch is dispatched OR explicitly paused
affects:
  - Plan/harness/restructure/spec.md
  - Plan/harness/restructure/_migration/checklist.md
  - servers/agency-mcp/src/agency_mcp/domains/_base/__init__.py
  - servers/agency-mcp/src/agency_mcp/domains/_base/domain.py
  - servers/agency-mcp/src/agency_mcp/domains/_base/state.py
  - servers/agency-mcp/src/agency_mcp/domains/_base/handlers.py
  - servers/agency-mcp/src/agency_mcp/domains/_base/manifest.py
  - servers/agency-mcp/src/agency_mcp/domains/_base/conventions.py
  - servers/agency-mcp/src/agency_mcp/domains/music/   # 17 handler modules + state + skills + tests
  - servers/agency-mcp/src/agency_mcp/domains/novel/   # 13 handler modules + state + tests
  - servers/agency-mcp/src/agency_mcp/domains/jules/   # 6 handler modules + state + skill + tests
  - servers/agency-mcp/src/agency_mcp/domains/context/ # 2 handler modules + state + tests
  - servers/agency-mcp/src/agency_mcp/domains/shared/  # 6 handler modules + state + tests
  - servers/agency-mcp/src/agency_mcp/server.py        # create_mcp() collapses to 5-line loop
  - tests/_harness/normalisation.py                    # removed — no longer needed
  - bin/agency-dev-install                             # skill walk path updated
  - Plan/000-overview.md                               # §7 target file structure updated
source-repos: []
estimated_jules_sessions: 6   # one per domain + one for _base + one for migration sweep
domain: agentic
wave: C
spec_kind: vision
tag_target: design/harness-v2-restructure
supersedes_in_part_of: [023]  # the daemon work that Plan/023 owned is in harness/design.md; this spec is orthogonal
---

> **Status:** `vision` — this is a "someday" 10/10 target. The active implementation path is `Plan/harness/design.md` Path A (9/10 via low-cost source levers + harness normalisation). This spec is on record so the path is visible and reviewable; it should not start until the Phase 2-8 surge from Plan/000-v2 has slowed enough that a 2-3 week refactor PR will not collide with concurrent Jules dispatches.
>
> **Working branch (when scheduled):** to be assigned. **Reference design:** `Plan/harness/design.md` §11.4 (Path B).

# Restructure for native isomorphism — `domains/<name>/` tree with `Domain` base class

## 1. Why

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

## 2. Done When

- [ ] `servers/agency-mcp/src/agency_mcp/domains/_base/` exists with the five base modules listed in `affects:`. Each base module ≤ 100 LOC.
- [ ] Each of the five concrete domains (`music`, `novel`, `jules`, `context`, `shared`) has its `__init__.py` exporting a `<Name>Domain(Domain)` subclass with `name`, `state_cls`, `handler_modules`, and `tool_only` declared.
- [ ] Each domain's handler modules have been ported to use `@tool(domain="X", ...)` from `_base/handlers.py` instead of bare `@mcp.tool(...)` or post-wrap `mcp.tool(...)(fn)`. Existing function bodies unchanged; only the decoration line changes.
- [ ] Each domain has a `state.py` exporting `<Name>State(DomainState)`. Today's `StateCache` (in `servers/agency-mcp/src/agency_mcp/state/cache.py`) gets a thin `MusicState` wrapper that delegates to it; full collapse of `StateCache` into `DomainState` is a follow-up.
- [ ] Each domain has a `tests/` subdirectory mirroring the current `tests/unit/<domain>/` layout. Test imports updated from `from agency_mcp.handlers.<domain>` to `from agency_mcp.domains.<domain>.handlers`.
- [ ] `servers/agency-mcp/src/agency_mcp/server.py` `create_mcp()` collapses to the five-line for-loop sketched in `Plan/harness/design.md` §11.4.
- [ ] `tests/_harness/normalisation.py` is **removed** — the `Domain` base class makes its two normalisation passes redundant. L1's `list_tools` / `dispatch_skill` delegate directly to the registered domains.
- [ ] `manifest.json` is fully regenerated by `_base.manifest.sync_manifest_from_registrations(mcp)`; the check-in version becomes a generated artefact with a clear header.
- [ ] `bin/agency-dev-install` line 53 (skill walk) updated to walk `servers/agency-mcp/src/agency_mcp/domains/*/skills/`.
- [ ] `Plan/000-overview.md` §7 "Target file structure" replaced with the new tree.
- [ ] `tests/integration/test_context_anchor_triad.py` still passes unchanged — the four-verb contract is preserved.
- [ ] Boot budget regression: `tools/list` payload size unchanged within ±5% (no perf regression from the abstraction).
- [ ] All ~50 affected test files compile and pass under the new import paths.
- [ ] `docs/architecture/domains.md` (NEW, ≤200 lines) describes the `Domain` base class contract and how a new domain is authored.

## 3. Target tree (canonical)

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
    │   └── conventions.py     # invariants:
    │                          #   - DOMAIN_RE = r'^[a-z]+$'
    │                          #   - TOOL_NAME_RE = r'^[a-z]+_[a-z_]+$'  (<domain>_<verb>)
    │                          #   - TAG_FMT = "domain:{name}"
    │                          #   - SKILL_SCHEMA = { name, description, model?, allowed-tools? }
    │                          #   - BinaryEnvelope = TypedDict[type, path, size_bytes, mime_type, sha256]
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

## 4. The `Domain` base class contract (full signature)

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

## 5. Migration strategy

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

## 6. Coordination with Plan/000-v2

This restructure **gates Phase 7 specs (015, 016, 018, 021)** if they have not yet dispatched at the time it's scheduled. The orchestrator's options:

- **Schedule before Phase 7.** Run the 8-PR sequence to completion, then dispatch Phase 7 against the new tree. Lowest conflict risk.
- **Schedule after Phase 7.** Let Phase 7 land in the old tree, then migrate the new handlers as part of PR 2-6. Higher conflict risk but unblocks Phase 7 in the short term.
- **Pause Phase 7 mid-dispatch.** Cancel in-flight Phase 7 Jules sessions, run the restructure, re-dispatch Phase 7 against the new tree. Highest cost.

Recommendation: **schedule after Phase 7 if Phase 7 is already in flight, before Phase 7 otherwise.** The eight-PR sequence is ~2-3 weeks elapsed; this is acceptable downtime between Phase 6 and Phase 7 but not between Phase 7's dispatch and merge.

`Plan/000-overview.md` §9 Phase 7 dispatch matrix must be updated by PR 8 to reference the new domain paths.

## 7. Out of scope

- **Per-tool refactoring.** Tool bodies stay exactly as they are today. The decorator changes, the import path changes, but the handler logic is untouched. The handler-modernisation work (e.g. converting raw-kwarg signatures to Pydantic models) is a separate spec family.
- **StateCache collapse.** `state/cache.py` keeps its current implementation; `MusicState` etc. are thin wrappers around it. A full collapse of `StateCache` into per-domain `DomainState` is a follow-up spec only if the indirection becomes painful.
- **Skill back-fill for context/novel/shared (lever L-η).** The `tool_only = True` flag formalises the no-skill choice for shared. Whether context/novel ever grow skills is a content decision, not this spec's.
- **Stateful-tool refactor (lever L-ε).** The `@tool(requires_state=[...])` decorator parameter exists in this spec but is opt-in per tool. The full audit of stateful tools and per-tool decisions stays in `Plan/harness/L-epsilon-stateful-tools.md`.
- **Binary-payload envelope (lever L-ζ).** `conventions.BinaryEnvelope` is defined here but not enforced on existing tools. The migration to standardised envelopes is `Plan/harness/L-zeta-binary-envelope.md`.
- **External-agent reachability (L3 work).** That's `Plan/harness/design.md` §5; this spec is orthogonal.

## 8. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Concurrent Phase 2-8 PRs conflict with PR 2-6 | High if scheduled mid-phase | Schedule after Phase 7 if Phase 7 is in flight; otherwise before |
| ~50 test files need import-path updates; manual rebase | High | PR 2-6 each include automated `sed` migration as part of the PR; mass-edit is mechanical |
| `manifest.json` runtime regeneration vs check-in version conflict | Medium | PR 1's `_sync_manifest` adds a header `"_meta": {"generated_by": "_base.manifest", "do_not_hand_edit": true}` to the generated section |
| Performance regression from `Domain.register()` abstraction overhead | Low | Boot-budget regression test in PR 1 asserts `tools/list` payload ±5%; fail loud on regression |
| Backward-compat shims linger after PR 7 | Medium | PR 7's checklist includes `grep -rln 'agency_mcp.handlers' --exclude-dir=domains` returning zero hits |
| The `Domain` abstraction proves wrong for a future domain (e.g. cross-cutting concern) | Low | `skill_root` override + `tool_only` flag already handle the two known divergences (agentic, shared); extension via additional class variables |

## 9. Dependencies

- `Plan/harness/design.md` — the active design's tag must land first. This spec consumes the four-verb contract and the L1+L3 implementation as substrate.
- Plan/000-v2 Phase 7 status — see §6 above.
- Plan/023 — the daemon work is in `Plan/harness/design.md` §5; this spec is orthogonal.

## 10. References

- [`Plan/harness/design.md`](../design.md) §11.4 — Path B summary that this spec elaborates
- [`Plan/harness/_research/05-domain-isomorphism.md`](../_research/05-domain-isomorphism.md) — the audit that motivated Path B
- [`Plan/000-overview.md`](../../000-overview.md) §7 — current target tree, replaced by §3 of this spec
- [`Plan/JULES_PROTOCOL.md`](../../JULES_PROTOCOL.md) §3 (branch/PR discipline), §8 (silent-fail recovery)
- [`Plan/JULES-REVIEW-LOOP.md`](../../JULES-REVIEW-LOOP.md) §4 — review-loop applied to each of the 8 PRs above

## 11. Status / next steps

This spec is **`vision`** status. It does NOT dispatch Jules. It's on record so:

1. Future reviewers can see the endgame design before it's scheduled.
2. The next time the orchestrator considers scope-creeping a handler refactor into Phase 7+, this spec is the place to land it cleanly.
3. When Phase 7 completes (or before, if the orchestrator chooses), this spec is promoted to `status: ready` and PR 1 of the eight-PR sequence dispatches per the JULES-REVIEW-LOOP.

Until then: the active path is `Plan/harness/design.md` Path A — L-α/β/γ landing alongside the L1+L3 implementation, with L-δ/ε/ζ/η as named follow-up sub-specs.