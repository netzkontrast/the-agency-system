# Research 05 — Per-domain isomorphism audit (2026-05-18)

> **Question.** Can a single four-verb contract (*list_tools, call_tool, list_skills, dispatch_skill*) be made isomorphic across the five domains music, novel, jules, context, shared — or does the handler diversity force per-domain divergence?
> **Answer.** Isomorphism survives at the *API surface* but five concrete strains require the design to handle them explicitly. **Uniformity score: 6/10 today; the harness design adds two normalisation passes that lift it to 9/10.**

This research file captures the parallel sub-agent audit done on 2026-05-18 (branch `claude/fix-pr-merge-issues-sn1CS`). Findings drove §3.7 and §5.9 of `Plan/harness/design.md`.

## 1. Per-domain inventory

| Domain | Handler modules | Tools (approx) | Skills | Manifest entries |
|---|---|---|---|---|
| `context` | 2 (`anchors.py`, `resources.py`) | 4 | 0 | 4 eager (`context_search`, `context_describe`, `context_read`, `context_changes`) — tagged `domain:cross` |
| `jules` | 6 (`lifecycle`, `aliases`, `bulk`, `patches`, `source`, `trim`) | ~18 | 1 (`skills/jules/SKILL.md`) | 16 deferred + 1 eager (`jules_quota`) |
| `music` | 17 (core/audio/content/ideas/promo/sheet_music/video/mixing/gates/...) | ~83 | 54 | 83 deferred + 2 eager (`music_health_check`, `plugin_help`) |
| `novel` | 13 (core/characters/content/ideas/status/revision/gates/promo/world/structure/...) | ~56 | 0 | **0 entries — handlers register at boot but manifest.json never lists them** |
| `shared` | 6 (`health`, `config`, `reference`, `search`, `session`, `skills`) | ~10 | 0 | 1 deferred + 1 eager (`health_check`) — one tool has `@mcp.tool` with **no tags** |
| `agentic` (cross-cutting) | n/a | 0 (skill-only domain) | 3 | n/a |

Cites: `servers/agency-mcp/src/agency_mcp/handlers/*/` listings; `servers/agency-mcp/src/agency_mcp/codemode/manifest.json` per-domain grouping.

## 2. Registration-pattern divergence

Three patterns coexist in the codebase:

```python
# Pattern A — named function with inline decorators (context, jules)
def register_context_anchor_tools(mcp: FastMCP) -> None:
    @mcp.tool(tags={"domain:cross", "anchor:context"})
    def context_search(...): ...

# Pattern B — bare `register(mcp)` exporting top-level functions wrapped after definition (music, novel)
def music_find_album(slug: str) -> str: ...
def register(mcp: Any) -> None:
    mcp.tool(tags={"domain:music"})(music_find_album)

# Pattern C — bare decorator without `tags=` (shared/health.py)
@mcp.tool
def health_check() -> str: ...
```

**Impact.** A harness that introspects `mcp.list_tools()` sees all three through the same FastMCP `Tool` surface. But scripts that walk filesystem to find registration sites (e.g. Spec 131's coverage lint) must handle all three. Pattern C is the worst offender — no `domain:*` tag means `list_tools(domain="shared")` excludes `health_check` unless the harness falls back to "no-tag = `domain:shared`".

## 3. Five concrete strain points

### Strain 1 — Complex parameter expressions

`music_master_album()` takes 6+ keyword args (`target_lufs: float`, `ceiling_db: float`, `cut_highmid: bool`, etc.). The L3 CLI's `--param key=value` syntax cannot express floats / bools / enums without ambiguity (`--param target_lufs=-14` vs. `--param target_lufs="-14"`).

**Harness response (design §5.3).** L3 CLI accepts `--json '{...}'` as an escape hatch for complex inputs. L1's `call_tool(name, **kwargs)` is naturally typed via Python and avoids this entirely. Documented in design §5.3 example block.

### Strain 2 — Non-JSON return paths

`music_transcribe_audio()` returns a `str` containing a `.pdf` file path; the binary payload lives on disk, not in `ToolResult.content[0].text`. Same for `music_generate_promo_videos()` returning `.mp4` paths.

**Harness response.** Both L1's `call_tool` and L3's `agency tool execute` return the JSON envelope verbatim — the file-path string is the body. Callers that need the binary fetch it via a separate `agency file get <path>` verb (deferred to L3 progressive-disclosure sub-spec). For L1 use, tests assert on the metadata, not the binary. Documented in design §5 "out of scope" and §3.5.

### Strain 3 — Skill-schema divergence

Music SKILL.md frontmatter:
```yaml
name: music-resume
description: Find an album by name and show detailed status.
argument-hint: <album-name>
model: claude-opus-4-7
allowed-tools: [Read, Edit, agency-system-mcp]
```

Jules SKILL.md frontmatter:
```yaml
name: silent-fail-recovery
description: >
  When a Jules session enters COMPLETED with no branch on origin…
```

`model` and `allowed-tools` are music-only. A naive `dispatch_skill(name) → {frontmatter}` returns heterogeneous shapes.

**Harness response (design §3.7).** Define a *harness-stable subset* of SKILL.md frontmatter: `{name (required), description (required), argument-hint (optional), model (optional), allowed-tools (optional)}`. `dispatch_skill` returns the full parsed frontmatter; callers reading optional fields get `None` rather than KeyError. A future `tests/smoke/test_skill_schema.py` (Phase 1 sibling spec, not this design) enforces the required-field contract across all 58 SKILL.md files.

### Strain 4 — Session-state dependency chains

`music_update_track_field()` requires the album's StateCache to be warm; without a prior `music_find_album()` (or `rebuild_state`), it returns "album not found". The dependency is implicit — not declared in the tool's schema.

**Harness response (design §3.7).** The harness's `harness_mcp()` singleton means a test session's StateCache persists across calls in pytest (and across requests in the L3 daemon). The order matters within one session; tests document the call sequence. A `harness_warm(domain)` helper is added as a convenience that triggers domain-specific cache-bootstrap (calls `music_list_albums()` for music, etc.). For L3, the daemon's process lifetime preserves the cache across CLI invocations until `agency server stop`.

### Strain 5 — Domain classifier / manifest divergence

- Context tools tagged `domain:cross` not `domain:context`.
- Novel domain has 56 handlers registered but **zero entries in `manifest.json`**.
- Shared's `health_check` has no tags at all.

`list_tools(domain="novel")` via manifest returns 0 tools. Via `mcp.list_tools()` walking `.tags`, returns the 56. The two answer disagree.

**Harness response (design §3.7).** The harness uses `mcp.list_tools()` (the FastMCP authoritative source — every registered tool is enumerated) as the source of truth, not `manifest.json` (the CodeMode-anchor classification cache). Manifest is consulted *only* for the `eager / deferred` boolean. A `list_tools(domain="novel")` returns the 56 novel tools regardless of manifest gaps. The novel-manifest gap is logged as a known issue (Spec 131 / Phase 1 lint will close it independently of this design).

## 4. Coverage of integration tests

| Domain | Has integration test calling `mcp.call_tool()`? | Canonical tool a smoke test could call |
|---|---|---|
| `context` | ✅ `tests/integration/test_context_anchor_triad.py:18-39` | `context_search` (covered) |
| `music` | ❌ | `music_list_albums()` — pure-read, no cache warmth required |
| `novel` | ❌ | `novel_list_works()` — pure-read |
| `jules` | ❌ | `jules_status_all()` — pure-read, idempotent |
| `shared` | partial (`test_boot.py` invokes via `get_tool`, not `call_tool`) | `health_check()` — degenerate input |

L1 makes adding these tests cheap (one fixture line + one `await tool(...)` per assertion).

## 5. Implications for the design

The four-verb contract survives, with two normalisation passes documented in §3.7 and §5.9 of the design:

1. **Source-of-truth normalisation.** `list_tools(domain=X)` queries `mcp.list_tools()` and filters by `domain:X` tag (or no-tag → `domain:shared` fallback). Manifest is consulted only for anchor/deferred classification, not for tool discovery.
2. **Schema-shape normalisation.** `dispatch_skill(name)` returns the full parsed frontmatter; callers tolerate optional fields being `None`. A future schema lint (Phase 1 sibling) enforces required fields.

The remaining strains (complex params, binary returns, session state) are handled via documented conventions rather than API changes:
- Complex params: L3 supports `--json '{...}'`; L1 has natural kwargs.
- Binary returns: callers fetch separately; harness returns paths.
- Session state: `harness_warm()` helper + documented call sequencing.

**Score post-design:** 9/10. The two normalisations close the manifest/tag gaps; the three documented conventions cover the rest without API change.

## References

- `servers/agency-mcp/src/agency_mcp/handlers/context/anchors.py:46-53` — Pattern A
- `servers/agency-mcp/src/agency_mcp/handlers/music/core.py:1140-1157` — Pattern B
- `servers/agency-mcp/src/agency_mcp/handlers/shared/health.py:14` — Pattern C (no tags)
- `servers/agency-mcp/src/agency_mcp/codemode/manifest.json` — domain coverage gaps
- `skills/music/resume/SKILL.md` — music frontmatter sample
- `skills/jules/SKILL.md` — jules frontmatter sample
- Parallel sub-agent verdict 2026-05-18 (this branch)
