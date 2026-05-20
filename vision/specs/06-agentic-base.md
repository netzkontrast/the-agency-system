---
slug: spec-06-agentic-base
type: impl-spec
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: Implementation spec for the agentic column base layer at `agentic/` (repo root). FastMCP harness + cell loader + four-verb contract + derivation rules + Code Mode bridge. No row-specific cells in this PR.
affects:
  - vision/specs/06-agentic-base.md
depends_on:
  - vision/specs/01-cell-manifest.md
  - vision/specs/02-tool-result-envelope.md
  - vision/specs/04-phase-state-envelope.md
  - vision/specs/08-context-base.md
referenced_by: []
implements_for_jules:
  - agentic/__init__.py
  - agentic/_bootloader.py
  - agentic/_harness/__init__.py
  - agentic/_harness/fastmcp_boot.py
  - agentic/_harness/cell_loader.py
  - agentic/_harness/name_deriver.py
  - agentic/_harness/codemode.py
  - tests/agentic/test_harness.py
  - tests/agentic/test_cell_loader.py
  - tests/agentic/test_name_deriver.py
---

# Spec 06 — Agentic Base Layer

> **STATUS — 2026-05-19**: ✅ **Implemented and merged** in PR #148. All `implements_for_jules:` files live at the repo root under `agentic/`. Cold-boot payload tested under 500 tokens. The four-verb contract is registered. **Open follow-up (C5)**: the context hooks (`context/_hooks/{pre,post}_tool_use.py`) need to be wired into `agentic/_bootloader.py::boot()` so they fire on every tool call — see `vision/04-nextsteps.md`.

## Purpose

The **agentic column base layer** is the row-agnostic FastMCP harness
that boots the matrix, glob-scans every cell's `manifest.toml`, derives
skill and tool names from `(row, column)`, and exposes the four-verb
cross-row dispatch contract.

The base layer **is**:

- A FastMCP server (`agency-system`) that boots in under 500 cold-load tokens.
- A cell loader that discovers cells across all three columns.
- The four always-on tools that constitute the cross-row dispatch contract.
- The `prefers_codemode` plumbing into FastMCP's Code Mode renderer.

The base layer **is not**:

- A row-specific handler (`agentic/music/handlers/*.py` lands later via the meta-row pipeline).
- The central routing skill `/agency` (spec 09).
- Hot reload (deferred per `02-plan.md` Agentic Q1).
- Workflow phase execution or gate evaluation (spec 07).
- Schema authoring (schemas live in `context/_shared/schemas/`, spec 08; the harness only imports them).

## Folder layout

The implementing PR ships exactly this tree under `agentic/` (no row folders yet):

```
agentic/
├── __init__.py
├── _bootloader.py                # plugin entrypoint: boots FastMCP, scans cells, registers
└── _harness/
    ├── __init__.py
    ├── fastmcp_boot.py           # FastMCP server creation, the four-verb contract
    ├── cell_loader.py            # glob-scans <col>/<row>/manifest.toml across the matrix
    ├── name_deriver.py           # the derivation rules from spec 01
    └── codemode.py               # prefers_codemode bridge
```

Tests live at `tests/agentic/`. No other paths are touched.

## Functional requirements

### 1. FastMCP boot

```python
# agentic/_bootloader.py
def boot() -> "FastMCP":
    """Plugin entrypoint. Builds the server, scans cells, registers everything."""
```

- Creates a FastMCP server named `agency-system`. Version read from `pyproject.toml` (`project.version`).
- Registers the four-verb contract tools with full schemas (anchor tools).
- Calls `cell_loader.discover()`; registers every discovered skill and tool with `defer_schema=True` so their JSON Schemas are NOT in the initial `tools/list` payload.
- Returns the configured server; the plugin host calls `.run()`.

### 2. Four-verb contract

`agentic/_harness/fastmcp_boot.py` registers four always-on tools with full schemas:

```python
def register_four_verb_contract(mcp: FastMCP, registry: CellRegistry) -> None:
    @mcp.tool(name="mcp__list_tools")
    def list_tools(row: str | None = None) -> ToolResult:
        """Return names of registered MCP tools, optionally filtered by row."""

    @mcp.tool(name="mcp__call_tool")
    def call_tool(name: str, args: dict) -> ToolResult:
        """Invoke a registered tool by name; pass through the envelope."""

    @mcp.tool(name="mcp__list_skills")
    def list_skills(row: str | None = None) -> ToolResult:
        """Return slash-command names of registered skills."""

    @mcp.tool(name="mcp__dispatch_skill")
    def dispatch_skill(name: str, args: dict) -> ToolResult | PhaseStateEnvelope:
        """Invoke a skill. If it triggers a workflow phase that yields,
        return the PhaseStateEnvelope (spec 04). Else return a ToolResult."""
```

`dispatch_skill` is the cross-row dispatch entry. When the called skill kicks off a workflow phase that yields, return the `PhaseStateEnvelope` verbatim from spec 04. When it completes synchronously, return a `ToolResult` from spec 02.

### 3. Cell loading

```python
# agentic/_harness/cell_loader.py
def discover(root: Path = Path(".")) -> CellRegistry:
    """Glob-scan all three columns for manifest.toml and build the registry."""
```

Glob patterns: `agentic/*/manifest.toml`, `workflow/*/manifest.toml`, `context/*/manifest.toml`. Internal folders (`_harness`, `_runner`, `_store`, `_shared`, etc.) are NOT matched because they begin with `_`.

For each manifest:

1. The context column's PreToolUse hook (spec 08) validates the file against the matching cell schema. On failure the loader logs and skips the cell — boot continues for other cells.
2. `[skills].exports` → register slash commands `/{row}-{export}`; body resolves to `agentic/{row}/skills/{export}/SKILL.md`.
3. `[tools].exports` → register MCP tools `mcp__{row}_{export}`; handler is lazily imported from `agentic.{row}.handlers.{export}.handle`. Tools register with `defer_schema=True`.
4. `[codemode].prefers` → record the derived tool names in `registry.codemode_set`.

This PR ships an **empty** matrix — `discover()` returns an empty registry. The four verbs still register.

### 4. Name derivation

`agentic/_harness/name_deriver.py` codifies spec 01's derivation rules. All other harness modules import from here — no string concatenation of names elsewhere.

```python
def skill_name(row: str, export: str) -> str:
    """('music','producer') -> 'music-producer'."""
    _assert_no_row_prefix(row, export)
    return f"{row}-{export}"

def mcp_tool_name(row: str, export: str) -> str:
    """('music','analysis') -> 'mcp__music_analysis'."""
    _assert_no_row_prefix(row, export)
    return f"mcp__{row}_{export}"

def skill_md_path(row: str, export: str) -> Path:
    return Path(f"agentic/{row}/skills/{export}/SKILL.md")

def handler_module(row: str, export: str) -> str:
    return f"agentic.{row}.handlers.{export}"
```

`_assert_no_row_prefix` raises `ManifestLintError` if `export` starts with `f"{row}-"` or `f"{row}_"`. The cell loader catches this and reports the cell as broken. Defense in depth: schema validation (spec 08) catches it at write time; the deriver catches it at boot time.

### 5. Tool return validation

Every registered tool's return value is validated against `tool_result.schema.json` (spec 02, owned by spec 08) before the harness hands it to FastMCP. On failure the harness wraps the return:

```python
{
    "ok": False,
    "data": {
        "error": {
            "code": "ENVELOPE_INVALID",
            "message": "<jsonschema error path>",
            "fix_hint": "Tool must return the spec-02 envelope.",
        }
    },
    "warnings": [],
    "next_suggested_tools": [],
}
```

The four-verb tools are themselves validated (meta-consistency). Per-tool `data` schemas (`context/_shared/schemas/tools/<row>_<verb>.schema.json`) apply additionally when present; failures surface as `DATA_SCHEMA_FAILED` per spec 02.

### 6. Code Mode bridge

```python
# agentic/_harness/codemode.py
def wrap_for_codemode(handler, tool_name: str, codemode_set: set[str]):
    """If tool_name in codemode_set, set prefers_codemode=True on the response."""
```

The base layer only plumbs the flag; FastMCP does the actual rendering. The harness reads `[codemode].prefers` during `discover()`, stores the fully-derived MCP tool names in `CellRegistry.codemode_set`, and on `mcp__call_tool` for a name in that set attaches `prefers_codemode=True` to the response envelope.

A skill's `prefers_codemode: true` frontmatter is honored separately on `mcp__dispatch_skill` — the harness reads the SKILL.md frontmatter at dispatch time.

## Cold-boot budget

Target: **system prompt + initial `tools/list` payload < 500 tokens**.

Enforcement:

- Only the four-verb tools register with full schemas. Every other tool uses `defer_schema=True`.
- The four schemas combined fit under ~400 tokens (measured during implementation). Server identification adds ~50 tokens. The remaining slack absorbs FastMCP framing.

Measurement command (CI):

```bash
python -m agentic._bootloader --emit-cold-boot | wc -c
```

`tests/agentic/test_harness.py` asserts the cold-boot payload length via `tiktoken` (cl100k tokenizer) — fails if `>= 500 tokens`. When future PRs add row cells, the budget must hold because deferred schemas keep their cost off the cold-boot path.

## Worked example

### Empty matrix (this PR's shipped state)

`agentic/` is the only column with files. No row manifests exist anywhere. Booting produces:

```
$ python -c "from agentic._bootloader import boot; boot()"
[agency-system] boot complete
[agency-system] tools registered: 4
  - mcp__list_tools
  - mcp__call_tool
  - mcp__list_skills
  - mcp__dispatch_skill
[agency-system] skills registered: 0
[agency-system] cold-boot payload: 412 tokens (budget 500)
```

`mcp__list_tools()` returns `{"ok": true, "data": {"tools": ["mcp__list_tools", "mcp__call_tool", "mcp__list_skills", "mcp__dispatch_skill"]}, "warnings": [], "next_suggested_tools": []}`. `mcp__list_skills()` returns the same envelope with `skills: []`.

### Synthetic single-cell (in `tests/agentic/test_cell_loader.py`)

A test fixture writes `agentic/music/manifest.toml`:

```toml
[cell]
row    = "music"
column = "agentic"

[skills]
exports = ["producer"]

[tools]
exports = ["analysis"]

[codemode]
prefers = ["analysis"]
```

Plus stubs at `agentic/music/skills/producer/SKILL.md` and `agentic/music/handlers/analysis.py` (with `handle()` returning a valid envelope). Booting produces:

```
[agency-system] tools registered: 5
  - mcp__list_tools         (anchor)
  - mcp__call_tool          (anchor)
  - mcp__list_skills        (anchor)
  - mcp__dispatch_skill     (anchor)
  - mcp__music_analysis     (deferred schema; codemode prefers)
[agency-system] skills registered: 1
  - /music-producer  -> agentic/music/skills/producer/SKILL.md
```

`mcp__call_tool("mcp__music_analysis", {...})` invokes the handler, validates the envelope, and attaches `prefers_codemode=True` because `mcp__music_analysis` is in the codemode set.

## Acceptance criteria (Gherkin)

```gherkin
Feature: Agentic base layer

  Scenario: Four-verb contract is always present
    Given a fresh boot of agency-system
    When the registered tool list is captured
    Then it contains exactly mcp__list_tools, mcp__call_tool,
         mcp__list_skills, mcp__dispatch_skill
    And those four tools register with full (non-deferred) schemas

  Scenario: Cell loader scans all three column globs
    Given manifests at agentic/r1, workflow/r1, context/r1
    When cell_loader.discover() runs
    Then all three manifests are visited
    And internal _harness, _runner, _store folders are NOT visited

  Scenario: Derivation rules are honored
    Given an agentic manifest with row="music" and skills.exports=["producer"]
    When the harness boots
    Then a slash command "/music-producer" is registered
    And its body resolves to agentic/music/skills/producer/SKILL.md
    And no other rewriting of the name occurs

  Scenario: Redundant row prefix in exports is rejected
    Given an agentic manifest with row="music" and skills.exports=["music-producer"]
    When the harness boots
    Then ManifestLintError is raised for that cell
    And the cell is skipped but boot continues for other cells

  Scenario: Cold-boot stays under budget
    Given an empty matrix
    When the cold-boot payload is measured
    Then the total token count is strictly less than 500
    And only the four anchor tools contribute non-deferred schemas

  Scenario: Tool return is validated against envelope schema
    Given a handler returns {"ok": true, "data": "not an object", ...}
    When the harness intercepts the return
    Then the harness wraps the return as
         {"ok": false, "data": {"error": {"code": "ENVELOPE_INVALID", ...}}, ...}
    And the wrapped envelope itself validates against tool_result.schema.json

  Scenario: Code Mode flag propagates from manifest
    Given a manifest declares [codemode] prefers = ["analysis"]
    When mcp__call_tool("mcp__<row>_analysis", {...}) is invoked
    Then the response carries prefers_codemode=True
    And FastMCP receives that flag for Code Mode rendering

  Scenario: Cross-row dispatch returns the right envelope type
    Given mcp__dispatch_skill targets a skill that triggers a workflow yield
    When the dispatch completes
    Then the response is a PhaseStateEnvelope per spec 04
    And the four-verb caller can resume the workflow with the envelope
```

## `affects:` allow-list for the implementation PR

When Jules implements this spec, the implementing PR's `affects:` MUST be exactly:

- `agentic/__init__.py`
- `agentic/_bootloader.py`
- `agentic/_harness/__init__.py`
- `agentic/_harness/fastmcp_boot.py`
- `agentic/_harness/cell_loader.py`
- `agentic/_harness/name_deriver.py`
- `agentic/_harness/codemode.py`
- `tests/agentic/test_harness.py`
- `tests/agentic/test_cell_loader.py`
- `tests/agentic/test_name_deriver.py`

Touching any file outside this list (including any other column's folder or `pyproject.toml`) is out of scope. If Jules feels the urge to edit another column, it must reply with a friction note and stop.

## Dependencies

- `vision/specs/01-cell-manifest.md` — manifest schema the cell loader parses, and derivation rules the name deriver implements.
- `vision/specs/02-tool-result-envelope.md` — envelope every tool return is validated against.
- `vision/specs/04-phase-state-envelope.md` — envelope shape `mcp__dispatch_skill` returns when a workflow phase yields.
- `vision/specs/08-context-base.md` — owns the JSON Schemas the harness imports (`tool_result.schema.json`, `agentic-cell.schema.json`, per-tool `data` schemas) and the PreToolUse hook the cell loader calls.
