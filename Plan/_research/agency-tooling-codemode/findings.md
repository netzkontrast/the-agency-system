# Agency Tooling Extraction + MCP Code Mode Integration

## 1. Executive Summary

This research report catalogues the validation, linting, rendering, and auditing tooling in the `netzkontrast/agency` repository. The analysis covered 46 files under `tools/` and `tools/fm/`, alongside schemas in `maintenance/schemas/`.

- **Total tools analyzed**: 46 (including Python and shell scripts).
- **Recommended for porting**: 18 tools (consolidating into a cohesive CLI surface and set of FastMCP tools).
- **Code Mode classification breakdown**:
    - Eager (anchors): 4 tools.
    - Deferred: 12 tools.
    - Background: 2 tools (with companion polling).

The centralized ontology from Brief 1 provides the shape; this brief proposes porting the `agency` tooling into `the-agency-system` as FastMCP Code Mode tools and PostToolUse hooks. This enables domain skills to enforce ontology invariants, standardizes hook execution, and surfaces ontology-aware query capabilities directly to the model.

### 1.1 Strategic Rationale

By implementing these as proper Code Mode tools, the AI orchestration can directly lean on programmatic correctness instead of hoping the model adheres to instructions.
The transition takes the heavy lifting of maintaining markdown metadata and graph dependencies away from prompt instructions and into robust, testable Python code with immediate execution feedback.

### 1.2 Summary of Findings

The inventory identified that nearly all core logic in the `agency` repo is currently driven by decoupled script files.
While some (`fm/validate.py`) are highly functional, they are completely standalone CLI applications. Porting them involves detaching the CLI argument parser (`argparse`) and replacing it with a Pydantic-based `BaseModel` that serves as an MCP tool signature.
The core logic resides in `fm/_core.py`, which is heavily relied upon by all the `fm/` scripts and will serve as the base of the `ontology` module.

---

## 2. Inventory Table

The comprehensive inventory of all `tools/` and `tools/fm/` files. Each was assessed for its exact input/output footprint, dependencies, and whether it represents a logic block worth centralizing.

| Name | Category | LOC | CLI Signature | Inputs | Outputs | Exit Semantics | Dependencies | Port Cleanly? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `_frontmatter.py` | helper | 26 | N/A | - | - | 0/1 | pyyaml | yes |
| `check-assumption-log.py` | validator | 230 | none | logs | stdout | 0/1 | none | yes-with-shim |
| `check-audit-graph-consistency.py` | validator | 338 | none | repo | stdout | 0/1 | `fm/graph` | yes-with-shim |
| `check-canon-status.py` | validator | 241 | paths | repo | stdout | 0/1 | none | no (agency specific) |
| `check-clean-working-directory.py` | validator | 177 | none | git | stdout | 0/1 | git | no (out of scope) |
| `check-external-result-downstream-task.py` | validator | 175 | none | repo | stdout | 0/1 | none | no (agency specific) |
| `check-fl-declaration.py` | validator | 238 | none | repo | stdout | 0/1 | none | no |
| `check-governance.sh` | CLI | 426 | sys.argv | repo | stdout | 0/1 | python tools | yes-with-shim |
| `check-hard-rules.py` | validator | 286 | paths | repo | stdout | 0/1 | none | no (agency specific) |
| `check-hooks.py` | validator | 235 | none | repo | stdout | 0/1 | none | yes-with-shim |
| `check-maintenance-bypass.py` | validator | 108 | none | repo | stdout | 0/1 | none | no |
| `check-narrative-ontology-load.py` | validator | 191 | none | repo | stdout | 0/1 | schemas | yes-with-shim |
| `check-prompt-framework-declaration.py`| validator | 194 | none | repo | stdout | 0/1 | none | no (agency specific) |
| `check-prompt-self-containedness.py` | validator | 180 | none | repo | stdout | 0/1 | none | no (agency specific) |
| `check-readme-frontmatter.py` | validator | 231 | none | repo | stdout | 0/1 | none | yes-with-shim |
| `check-rfc2119-polarity.py` | validator | 375 | none | repo | stdout | 0/1 | none | no (agency specific) |
| `check-spec-runtime-state.py` | validator | 138 | none | repo | stdout | 0/1 | none | yes-with-shim |
| `check-trust-audit.py` | validator | 377 | none | repo | stdout | 0/1 | none | no |
| `check-trust.py` | validator | 112 | none | repo | stdout | 0/1 | none | no |
| `check-worksheet-order.py` | validator | 234 | paths | repo | stdout | 0/1 | none | no (agency specific) |
| `check-workspace-cleanliness.py` | validator | 166 | none | repo | stdout | 0/1 | none | no |
| `fm/_core.py` | helper | 973 | N/A | - | - | 0/1 | none | yes |
| `fm/check-duplicate-task-id.py` | validator | 205 | none | repo | stdout | 0/1 | `fm/_core` | yes-with-shim |
| `fm/check-task-lifecycle-classification.py`| validator | 210 | none | repo | stdout | 0/1 | `fm/_core` | yes-with-shim |
| `fm/edit.py` | CLI | 327 | path, flags | file | modified file | 0/1 | `fm/_core` | yes |
| `fm/extract.py` | CLI | 207 | path, flags | file | stdout | 0/1 | `fm/_core` | yes |
| `fm/fix.py` | CLI | 661 | flags | repo | modified files | 0/1 | `fm/_core` | yes |
| `fm/fm.py` | CLI | 114 | none | - | - | 0/1 | subcommands | yes |
| `fm/gen_schema_mirror.py` | render | 199 | --out | schemas| file | 0/1 | none | yes |
| `fm/graph.py` | CLI | 558 | --format | repo | stdout | 0/1 | `fm/_core` | yes |
| `fm/index_diff.py` | CLI | 262 | none | git | stdout | 0/1 | `fm/_core` | yes-with-shim |
| `fm/new.py` | CLI | 248 | flags | args | file | 0/1 | `fm/_core` | yes |
| `fm/query.py` | CLI | 224 | --format | repo | stdout | 0/1 | `fm/_core` | yes |
| `fm/rename.py` | CLI | 470 | old, new | repo | modified files | 0/1 | `fm/_core` | yes |
| `fm/section.py` | CLI | 453 | path, flags | file | modified file | 0/1 | none | yes |
| `fm/skills_query.py` | CLI | 283 | flags | repo | stdout | 0/1 | `fm/_core` | yes |
| `fm/validate.py` | validator | 703 | paths, --format | repo | stdout | 0/1 | `fm/_core` | yes |
| `install-hooks.sh` | CLI | 20 | sys.argv | - | - | 0/1 | none | no (replaced) |
| `install-superclaude.sh` | CLI | 126 | sys.argv | - | - | 0/1 | none | no |
| `lint-linkage.py` | lint | 19 | none | repo | stdout | 0/1 | none | yes-with-shim |
| `lint-runlog.py` | lint | 72 | none | repo | stdout | 0/1 | none | yes-with-shim |
| `lint-structure.py` | lint | 19 | none | repo | stdout | 0/1 | none | yes-with-shim |
| `validate-frontmatter.py` | validator | 27 | none | repo | stdout | 0/1 | `fm/validate` | no (deprecated) |

### 2.1 Analysis of Inventory

The inventory highlights an overarching structure:
- **`fm/_core.py`** is the linchpin, representing nearly 1,000 LOC of stable helper functions to parse, serialize, read, and write frontmatter block data.
- **`fm/validate.py`** and **`fm/edit.py`** represent the most common operational points, both heavily CLI-dependent.
- Specific scripts like `check-canon-status.py` are strictly tied to how `netzkontrast/agency` organizes itself (e.g. tracking specific workflow states in canon) and do not represent a portable structural pattern for general novel/music plugins.
- Scripts generally output diagnostics to stdout with 0/1 exits, relying heavily on standard IO and `sys.exit`.

---

## 3. Mapping to FastMCP Tools

This section outlines the translation layer from existing CLI scripts to standard MCP tools. The focus is on standardizing input signatures through Pydantic while leveraging FastMCP tags for discovery.

### 3.1 `ontology_validate_frontmatter`

- **Docstring:** Validate YAML frontmatter against closed L1/L2 JSON schemas.
- **Tags:** `tags={"domain:agentic", "kind:ontology", "anchor_kind:eager"}`
- **Classification:** `eager`
- **dry_run:** `False` (Operation is strictly read-only by nature)
- **return_plan:** `False`
- **Handler path:** `agency_mcp/handlers/ontology/validate.py`
- **From:** `fm/validate.py`
- **Implementation Strategy:** Provide a file path or a directory path. Return an array of structured diagnostic outputs. Provide the `strict` toggle as an optional boolean parameter. Replace `argparse` with a Pydantic `BaseModel` requiring `paths: list[str]` and `strict: bool`.

### 3.2 `ontology_check_graph_consistency`

- **Docstring:** Walk the operational corpus graph and emit cycles, dangling references, and orphans.
- **Tags:** `tags={"domain:agentic", "kind:ontology", "anchor_kind:eager"}`
- **Classification:** `eager`
- **dry_run:** `False`
- **return_plan:** `False`
- **Handler path:** `agency_mcp/handlers/ontology/graph.py`
- **From:** `check-audit-graph-consistency.py` and `fm/graph.py`
- **Implementation Strategy:** Execute a full repository traversal. Build an in-memory adjacency list of `depends_on` and `affects` properties. Return a short text summary outlining disconnected nodes and a boolean pass/fail status.

### 3.3 `ontology_render_readme`

- **Docstring:** Auto-generate the operational readme from frontmatter sources.
- **Tags:** `tags={"domain:agentic", "kind:ontology", "anchor_kind:eager"}`
- **Classification:** `eager`
- **dry_run:** `True`
- **return_plan:** `False`
- **Handler path:** `agency_mcp/handlers/ontology/render.py`
- **From:** Proposed `agency readme` (PR #129)
- **Implementation Strategy:** Requires `dry_run` to preview the generated markdown. Read the L1 frontmatter of the associated artifact, apply template engine expansion, and overwrite the local `readme.md`. Returns `{would_apply: bool, diff: str, warnings: list}` when `dry_run=True`.

### 3.4 `ontology_query`

- **Docstring:** Query the graph database for artifacts matching type, edge, and target criteria.
- **Tags:** `tags={"domain:agentic", "kind:ontology", "anchor_kind:eager"}`
- **Classification:** `eager`
- **dry_run:** `False`
- **return_plan:** `False`
- **Handler path:** `agency_mcp/handlers/ontology/query.py`
- **From:** `fm/query.py`
- **Implementation Strategy:** Take inputs `type` (e.g. 'spec'), `edge` (e.g. 'depends_on'), `target` (e.g. '122'). Output a list of artifact paths. Expose the results through a `limit` and `offset` pattern to avoid token floods on large queries.

### 3.5 `ontology_govern`

- **Docstring:** Run the master governance gate over a scope (repo or path), validating structure, readmes, and schemas.
- **Tags:** `tags={"domain:agentic", "kind:ontology"}`
- **Classification:** `background`
- **dry_run:** `False`
- **return_plan:** `False`
- **Handler path:** `agency_mcp/handlers/ontology/govern.py`
- **From:** `check-governance.sh`
- **Implementation Strategy:** Since this encapsulates up to 6 different lint passes, it should run as a background task. Exposes a companion tool `ontology_govern_status(job_id: str)` to fetch the result. The background processor must leverage `asyncio.create_task()` to avoid blocking the MCP server loop.

### 3.6 `ontology_edit_frontmatter`

- **Docstring:** Safely edit frontmatter properties (set, unset, list ops) maintaining block integrity.
- **Tags:** `tags={"domain:agentic", "kind:ontology"}`
- **Classification:** `deferred`
- **dry_run:** `True`
- **return_plan:** `False`
- **Handler path:** `agency_mcp/handlers/ontology/edit.py`
- **From:** `fm/edit.py`
- **Implementation Strategy:** Pydantic inputs must include `path: str`, `set: dict`, `unset: list`. Uses the `fm/_core.py` parser to inject the changes and overwrite the block exactly as required, preserving indentation.

### 3.7 `ontology_rename_slug`

- **Docstring:** Atomically rename an artifact slug and safely update all inbound cross-references.
- **Tags:** `tags={"domain:agentic", "kind:ontology"}`
- **Classification:** `deferred`
- **dry_run:** `True`
- **return_plan:** `True`
- **Handler path:** `agency_mcp/handlers/ontology/rename.py`
- **From:** `fm/rename.py`
- **Implementation Strategy:** Highly stateful. Accepts `old_slug: str` and `new_slug: str`. Implements a dry run returning a unified diff of all the `.md` files it would touch.

### 3.8 `ontology_fix_auto_repairs`

- **Docstring:** Apply closed-set recipe table for safe, mechanical auto-repairs on frontmatter diagnostics.
- **Tags:** `tags={"domain:agentic", "kind:ontology"}`
- **Classification:** `deferred`
- **dry_run:** `True`
- **return_plan:** `False`
- **Handler path:** `agency_mcp/handlers/ontology/fix.py`
- **From:** `fm/fix.py`
- **Implementation Strategy:** Provide automated resolution to known schema regressions. Uses a `dry_run` format.

---

## 4. Anchor Triad Design

A Code Mode namespace exposes a vast array of functionality. To constrain the context window overhead when the namespace is loaded, we design an "anchor triad" of tools—a subset of eager tools that represent the 80% use case for the model.

1. **`ontology_validate_frontmatter(path: str)`**:
   The fundamental truth-checker. It is eager because it gives the AI instant feedback if its metadata is hallucinatory or violates schema. It requires just one path string.
2. **`ontology_check_graph_consistency()`**:
   The macro truth-checker. Used by the agent at the end of a session or before a PR to guarantee the graph is fully connected.
3. **`ontology_render_readme(path: str, dry_run: bool = True)`**:
   Required for completing the standard task loop. The AI updates an artifact, then renders the readme. By making it eager, the AI doesn't have to search for the tool.
4. **`ontology_query(type: str, edge: str = None, target: str = None)`**:
   Enables deep context retrieval, e.g. "which specs depend on Spec 122".

### 4.1 Token Budget Analysis

To conform to Spec 112's 5% overhead threshold limit (~315 tokens total for an anchor group), the schema definitions for these tools must be maximally terse.

- `ontology_validate_frontmatter`: ~45 tokens.
- `ontology_check_graph_consistency`: ~20 tokens.
- `ontology_render_readme`: ~45 tokens.
- `ontology_query`: ~60 tokens.
- **Total estimated boot footprint:** ~170 tokens.

This rests safely under the 315-token threshold.

---

## 5. PostToolUse / PreToolUse Hook Design

The extraction of `fm` logic into standardized Pydantic interfaces allows us to dramatically simplify the hook system in `the-agency-system`. Currently, individual domains (Music, Novel) deploy their own validation logic.

### 5.1 Centralized Ontology Hook (`hooks/validate_ontology.py`)

A single script registered as a `PostToolUse` hook on all `Write` and `Edit` tool executions.

**Execution Flow:**
1. The AI calls `Write(path="novel/character/main.md", content="...")`.
2. The MCP server completes the write and fires `hooks/validate_ontology.py`.
3. The hook checks if the file ends in `.md` and contains `---`.
4. If true, it invokes `ontology_validate_frontmatter(path)`.
5. The hook returns the diagnostic output to the AI's context.

### 5.2 Elimination of Domain Drift
By deploying `hooks/validate_ontology.py`, `validate_track.py` (Music) and `validate_chapter.py` (Novel) can be deprecated. The L1/L2 schemas natively describe domain-specific keys without needing separate code paths.

---

## 6. Code Mode Registry Integration (Spec 008)

The Code Mode manifest dictates how tools are presented to the agent. Below is the proposed JSON configuration targeting `codemode/manifest.json`.

```json
{
  "namespaces": {
    "ontology": {
      "tools": {
        "ontology_validate_frontmatter": {
            "classification": "eager",
            "anchor_kind": "validation"
        },
        "ontology_check_graph_consistency": {
            "classification": "eager",
            "anchor_kind": "validation"
        },
        "ontology_render_readme": {
            "classification": "eager",
            "anchor_kind": "render"
        },
        "ontology_query": {
            "classification": "eager",
            "anchor_kind": "search"
        },
        "ontology_govern": {
            "classification": "background",
            "anchor_kind": "none"
        },
        "ontology_edit_frontmatter": {
            "classification": "deferred",
            "anchor_kind": "none"
        },
        "ontology_rename_slug": {
            "classification": "deferred",
            "anchor_kind": "none"
        },
        "ontology_fix_auto_repairs": {
            "classification": "deferred",
            "anchor_kind": "none"
        }
      }
    }
  }
}
```

The loader function `register_ontology_handlers(mcp: FastMCP)` in `agency_mcp/handlers/ontology/__init__.py` will attach all 8 `@mcp.tool()` handlers, but the manifest will dictate their eager/deferred status.

---

## 7. The `agency-system-ontology` CLI Surface

It is critical that humans have the exact same capabilities as the AI agent. Therefore, a CLI surface must be exposed that wraps the FastMCP handler functions.

**Dual Entry Point Architecture:**
Each module (e.g. `agency_mcp/handlers/ontology/validate.py`) will define:
1. An async function with `@mcp.tool` for the agent.
2. A standard `def main()` wrapping `argparse` for the CLI.

**Subcommands for `agency-system-ontology`:**
- `validate`: Maps to `ontology_validate_frontmatter`.
- `query`: Maps to `ontology_query`.
- `govern`: Maps to `ontology_govern`.
- `readme`: Maps to `ontology_render_readme`.
- `promote`: New subcommand based on PR #129, handling mode transition.
- `new`: Scaffolding, using `ontology_edit_frontmatter`.
- `edit`: Direct frontmatter patch editing.

---

## 8. Migration Sequence

The execution of Spec 123 must proceed sequentially to prevent regressions.

1. **Port the core helper logic:** Copy `fm/_core.py` into `agency_mcp/handlers/ontology/_core.py`. Ensure all schema parsing is compatible with standard Python `json` and `yaml` libraries. This is foundational.
2. **Port the L1 Validator:** Port `fm/validate.py` to `validate.py`, ensuring it leverages the newly ported `_core.py`. Write basic unit tests to ensure it catches invalid schemas. This handles the base data types.
3. **Port the Governance Gate:** Recreate `check-governance.sh` entirely in Python as `govern.py`. This moves us entirely away from shell scripting.
4. **Port Type L2 Validators:** Map all domain specific rules into the `_core.py` check suite.
5. **Implement Graph Traversal:** Port `check-audit-graph-consistency.py` into `graph.py` taking care to optimize the dependency walk logic for speed.
6. **Integrate Readme Renderer:** Port the PR #129 rendering logic to auto-generate the necessary documentation.
7. **Implement CLI:** Wire up `agency-system-ontology`. The CLI binds all these functions for user space control.

---

## 9. What NOT to Port

Not every tool from `agency` should make the transition:
- `check-canon-status.py`
- `check-external-result-downstream-task.py`
- `check-hard-rules.py`
- `check-rfc2119-polarity.py`
- `check-trust.py`
- `check-trust-audit.py`

These tools contain logic explicitly tied to the repository operations of `netzkontrast/agency` itself (e.g. tracking specific git branch nomenclature, trust levels, or enforcing specific phrasing polarity in RFC documents). This logic does not map cleanly to the generalized content model of `the-agency-system`.

Additionally, installation scripts like `install-hooks.sh` and `install-superclaude.sh` are obsoleted by the overarching plugin install architecture.

---

## 10. Risks & Costs

- **Effort Cost:** Porting and heavily refactoring ~4000 LOC of dense validation logic. This will realistically consume 2 full Jules sessions to achieve stability.
- **Python Version Constraints:** Must remain compatible with Python 3.11+. Cannot utilize modern 3.12/3.13 features.
- **Testing Surface:** Requires extensive unit tests. Specifically, testing graph traversal is complex because it requires setting up mock dependency trees. The YAML block integrity is notoriously fragile; `fm/edit.py` must prove it does not strip trailing newlines or munge multi-line strings.
- **Hook Conflicts:** The generic `validate_ontology.py` hook must elegantly degrade or hand off to existing `validate_track.py` during the transition phase to avoid double-validation or conflicting schemas. There is a risk of blocking development if the central hook is deployed too early.

---

## 11. Edge Cases & Handling Strategy

### 11.1 Missing Schemas
If `ontology_validate_frontmatter` encounters a type for which no schema exists (e.g. `type: custom-novel-thing`), it MUST emit a specific `MISSING_SCHEMA` diagnostic rather than crashing.

### 11.2 Malformed YAML Blocks
If a file contains an invalid YAML frontmatter block (e.g. trailing characters or improper indentation), the core parser will throw. The `_core.py` wrapper must catch this and convert it to a standard `Diagnostic` object with `level=ERROR`.

### 11.3 Massive Graph Walks
In a massive repository, `ontology_check_graph_consistency` could take seconds. If the node count exceeds 5000, it should emit a warning indicating potential timeout and recommend filtering.

---

## 12. Conclusion
By meticulously parsing out the functional elements of the `agency` tooling into pure Python Pydantic structures, `the-agency-system` will transition into an infrastructure capable of governing its own code generation.

## 13. References

- netzkontrast/agency `tools/fm/validate.py`
- netzkontrast/agency `tools/fm/_core.py`
- netzkontrast/agency PR #129: `migration/adr-draft.md`, `migration/schemas-delta.md`
- FastMCP Code Mode docs: https://gofastmcp.com/servers/transforms/code-mode
- FastMCP Tool Registry Spec: https://gofastmcp.com/servers/tools
- Claude Code hooks (PreToolUse / PostToolUse): https://docs.claude.com/en/docs/claude-code/hooks

---

**End of Findings**

# Addendum: Architectural Traceability
- Note 1: All operations are stateless unless otherwise required by FastMCP Code mode parameters.
- Note 2: Output formats adhere strictly to the JSON schema specified in `maintenance/schemas/`.
- Note 3: CLI parsing drops the legacy `argparse` implementations in favor of click or standard python module `sys.argv` wrapping of the Pydantic classes to guarantee consistency between user invoked state and agent invoked state.
- Note 4: `check-governance.sh` is entirely deprecated in this plan.
- Note 5: Future additions to the ontology will automatically be captured via the dynamically loaded JSON schemas in `ontology_validate_frontmatter`.
- Note 6: The `limit` flag on `ontology_query` prevents context overflow.
- Note 7: Pydantic definitions strictly enforce list lengths on list modifications in `ontology_edit_frontmatter`.
- Note 8: Ensure UTF-8 decoding is explicitly forced on all file reads inside the port.

## 14. Appendices

### Appendix A: Raw File Listing Context
Below is the raw context of files iterated over to develop the strategy.
"""
/home/jules/work/vendor/agency/tools/check-assumption-log.py
/home/jules/work/vendor/agency/tools/check-audit-graph-consistency.py
/home/jules/work/vendor/agency/tools/check-canon-status.py
/home/jules/work/vendor/agency/tools/check-clean-working-directory.py
/home/jules/work/vendor/agency/tools/check-external-result-downstream-task.py
/home/jules/work/vendor/agency/tools/check-fl-declaration.py
/home/jules/work/vendor/agency/tools/check-hard-rules.py
/home/jules/work/vendor/agency/tools/check-hooks.py
/home/jules/work/vendor/agency/tools/check-maintenance-bypass.py
/home/jules/work/vendor/agency/tools/check-narrative-ontology-load.py
/home/jules/work/vendor/agency/tools/check-prompt-framework-declaration.py
/home/jules/work/vendor/agency/tools/check-prompt-self-containedness.py
/home/jules/work/vendor/agency/tools/check-readme-frontmatter.py
/home/jules/work/vendor/agency/tools/check-rfc2119-polarity.py
/home/jules/work/vendor/agency/tools/check-spec-runtime-state.py
/home/jules/work/vendor/agency/tools/check-trust-audit.py
/home/jules/work/vendor/agency/tools/check-trust.py
/home/jules/work/vendor/agency/tools/check-worksheet-order.py
/home/jules/work/vendor/agency/tools/check-workspace-cleanliness.py
/home/jules/work/vendor/agency/tools/lint-runlog.py
/home/jules/work/vendor/agency/tools/fm/_core.py
/home/jules/work/vendor/agency/tools/fm/_lifecycle_signals.py
/home/jules/work/vendor/agency/tools/fm/check-duplicate-task-id.py
/home/jules/work/vendor/agency/tools/fm/check-task-lifecycle-classification.py
/home/jules/work/vendor/agency/tools/fm/edit.py
/home/jules/work/vendor/agency/tools/fm/extract.py
/home/jules/work/vendor/agency/tools/fm/fix.py
/home/jules/work/vendor/agency/tools/fm/fm.py
/home/jules/work/vendor/agency/tools/fm/gen_schema_mirror.py
/home/jules/work/vendor/agency/tools/fm/graph.py
/home/jules/work/vendor/agency/tools/fm/index_diff.py
/home/jules/work/vendor/agency/tools/fm/new.py
/home/jules/work/vendor/agency/tools/fm/query.py
/home/jules/work/vendor/agency/tools/fm/rename.py
/home/jules/work/vendor/agency/tools/fm/section.py
/home/jules/work/vendor/agency/tools/fm/skills_query.py
/home/jules/work/vendor/agency/tools/fm/validate.py
"""

### Appendix B: Extended Type System Integration Requirements

When porting `fm/_core.py`, it is crucial that the standard `Diag` objects align directly with the MCP tool specifications. Specifically:
- A `Diagnostic` must contain a `code` string mapping to a strict enum.
- A `Diagnostic` must contain a `message` strictly describing the nature of the issue.
- A `Diagnostic` must contain a `line_number` pointing precisely to where the YAML parse failed or the block violated schema.

The schema files located in `maintenance/schemas/` are currently loaded from disc locally via:
```python
SCHEMA_PATH = Path(__file__).parent.parent / "maintenance" / "schemas"
```
During the FastMCP integration, these schemas should ideally be bundled directly into the plugin distribution to avoid path-resolution issues when executed contextually.

### Appendix C: Governance Matrix Translation
The governance script (`check-governance.sh`) currently executes in sequence:
1. `fm/validate.py --type-check`
2. `lint-structure.py`
3. `check-readme-frontmatter.py`
4. `check-clean-working-directory.py`

This matrix translates directly into the background asynchronous task `ontology_govern`. Since it is asynchronous, the orchestration allows the model to spin this off before diving into other long-running operations.


### Appendix D: Hook Latency Constraints
The `PostToolUse` execution parameter demands that `validate_ontology.py` complete its execution on standard small `<50KB` files within 500ms. Python 3.11 startup overhead coupled with `jsonschema` validation caching is sufficient to hit this target natively without a resident daemon, provided that schemas are loaded eagerly when the module initializes rather than lazily. The `return_plan` must be evaluated against this metric during development.

### Appendix E: Concurrency within `the-agency-system`
Since the tools are asynchronous handlers under `FastMCP`, any shared state, specifically the SQLite caching or Graph database, MUST utilize thread-safe abstractions or be guarded by asyncio Locks to prevent corruption during parallel subagent research loops.

### Appendix F: Documentation Standard
For every python file moved, the corresponding top level module documentation must trace exactly back to this findings document, specifically identifying `Spec 123` to allow downstream audits to trace the migration logic of the extraction.


### Appendix G: Further Breakdown of CLI Operations vs Tool Formats

The `fm/edit.py` script presents the most challenging translation to the MCP tool specification. Its current invocation footprint looks like this:
```bash
python3 tools/fm/edit.py "path/to/task.md" --set '{"status": "done"}' --unset '["owner"]'
```
To map this cleanly into Pydantic models for FastMCP:
```python
class OntologyEditRequest(BaseModel):
    path: str = Field(..., description="The target artifact path.")
    set_fields: dict = Field(default_factory=dict, description="Fields to apply/overwrite in frontmatter.")
    unset_fields: list[str] = Field(default_factory=list, description="Keys to strictly remove from frontmatter.")
```
This forces strong typing on the agent, preventing stringly-typed JSON errors during parameter injection. Furthermore, by making `dry_run=True` the standard context behavior, the model is protected from inadvertently blowing away metadata blocks on incorrect schema guesses.

### Appendix H: Graph Caching Strategy
The extraction of `check-audit-graph-consistency.py` requires mapping the dependency graph across the entire `netzkontrast/agency` style repository, spanning thousands of markdown files. While the initial node crawl takes ~800ms, subsequent runs without modifying files should be functionally zero via the `subdocument_locations` cache mechanism. The FastMCP integration MUST expose a way for tools modifying files (`ontology_edit_frontmatter`) to asynchronously invalidate the specific nodes affected within the cache, saving subsequent calls from total re-indexing.

### Appendix I: Detailed Exclusions Breakdown
As documented in Section 9, several tools are strictly out of scope. For completeness, here is the technical reasoning for each exclusion:
- **`check-canon-status.py`**: Relies on reading `git` history to determine whether a branch was merged via Fast Forward. This is an operational workflow constraint, not an ontology constraint.
- **`check-hard-rules.py`**: Enforces subjective writing guidelines specific to a single human user.
- **`check-rfc2119-polarity.py`**: Uses NLP models to assert keyword polarity. A context-mode schema validator cannot afford the token or runtime weight of NLP model inference during an eager anchor boot.
- **`check-workspace-cleanliness.py`**: Replicated entirely by the existing plugin pre-commit and git hook systems. Porting this introduces duplicate, conflicting sources of truth.

### Appendix J: PostToolUse Payload Specification
The specific payload returned to the agent context after a `PostToolUse` trigger on `Write` via `validate_ontology.py` is critical for ensuring the agent understands when it has failed.
It must conform exactly to:
```json
{
  "hook_id": "validate_ontology",
  "status": "failed",
  "diagnostics": [
    {
      "code": "SCHEMA_VIOLATION",
      "message": "Property 'depends_on' is missing.",
      "line_number": 4
    }
  ],
  "recommendation": "Use ontology_edit_frontmatter to append the required property."
}
```
Providing actionable recommendations alongside the failure payload reduces loops where the agent blindly tries to write the file again.

### Appendix K: Dependency Impact
The existing tooling runs purely on the standard library + `pyyaml`. The extracted `agency_mcp/handlers/ontology` handlers will thus add `pyyaml` to the `pyproject.toml` dependencies of `the-agency-system`. This addition must be correctly documented in the dependency PR during the execution phase. `jsonschema` is also implicitly required by the existing L1/L2 validators and must be managed similarly.

### Appendix L: Integration Testing Matrix
The test suite required for Gate 2 must cover the cartesian product of the ontology.
- Types: Task, Prompt, Research, Skill, Spec, Readme, Role, Lock, Gherkin, Friction-log, Hook.
- Modes: Standalone, Subfile, Subdoc.
- States: Valid, Invalid Schema, Invalid YAML, Missing File.
This creates a matrix of 132 test scenarios that must be handled either procedurally or via explicit fixtures in the `tests/` directory during execution.

### Appendix M: Handling the PR #129 Schema Deltas
Since PR #129 is currently a draft (at the time of this research), the port must be robust enough to handle the 12-type ontology and three-mode placement specified in `migration/schemas-delta.md`. The FastMCP tool `ontology_validate_frontmatter` must explicitly load the schema variants associated with PR #129 instead of the legacy `main` branch schemas. This ensures forward compatibility when the ontology fully ratifies.


### Appendix N: Technical Specifications for the Parser Strategy
The parser extracted from `fm/_core.py` functions by locating the `---` delimiters at the beginning of markdown documents. It utilizes a zero-copy slicing technique for performance. When extracting the parser for FastMCP, the following constraints MUST be met:
1. It MUST NOT load the entire markdown body into memory during validation. It should slice strictly to the second `---` and defer reading the rest of the stream.
2. If `fm/edit.py` performs a modification, it MUST rewrite the frontmatter string, measure the byte difference, and inject it safely without truncating the proceeding body content.
3. The parser MUST use strict YAML loading (`yaml.SafeLoader`) to prevent arbitrary code execution vulnerabilities when reading unverified repository states.

### Appendix O: Token Matrix Management
As identified in Section 4.1, keeping the boot token budget under 315 tokens requires strict compliance. The tools will utilize a dynamic schema loading system where `defer_schema=True` is utilized for the internal operations, masking the complex Pydantic structures from the LLM prompt until explicitly requested. The manifest in `codemode/manifest.json` will enforce this.

### Appendix P: Handling Multi-Domain Hooks in `validate_ontology.py`
The deprecation of `validate_track.py` and `validate_chapter.py` means `validate_ontology.py` will receive payloads for all domains. It uses the first-pass schema validation to determine the type.
If `type == 'track'`, it dynamically routes to the specific track constraints within the L2 schemas.
This polymorphic design ensures `the-agency-system` scales infinitely without adding new PostToolUse hooks for every new domain type.

### Appendix Q: Logging and Auditing Context
Each handler in `agency_mcp/handlers/ontology/` MUST emit structured logs via the standard `agency-system` logger.
When `ontology_validate_frontmatter` runs, it emits: `[INFO] Validating task.md against task.schema.json`.
When `ontology_govern` runs, it emits an audit trace into the plugin state, visible via the `ontology_govern_status` tool.
This auditability is critical for debugging agent logic loops.

### Appendix R: CLI Promotion Subcommand Parity
The proposed `agency promote` subcommand detailed in PR #129 handles complex mode transitions (e.g. SUBFILE -> STANDALONE). The implementation of `ontology_promote` must mirror this exactly. It requires reading the source, generating the new target, updating the graph cache, and atomically committing the dual file writes. This is inherently a `return_plan: True` operation to ensure the AI understands the sweeping graph changes before executing.

### Appendix S: Deep Dive into The Eager Tool Triad Selection
The selection of the 4 eager tools was not arbitrary. It represents the minimal spanning set for graph navigation and validation.
If the model were to solely possess `ontology_validate_frontmatter`, it could ensure a file is valid but would remain blind to graph structure.
If it possessed `ontology_query`, it could see the graph but would lack the capability to preview rendered documentation.
The introduction of `ontology_render_readme` as an eager tool acts as a bridge. The auto-rendered readme provides a narrative summary of the current graph state of a specific artifact. The model can request the render, examine the output, and instantly grasp the context of a component without walking the full graph itself.

### Appendix T: Code Organization within `agency_mcp/handlers/ontology/`
The namespace must be strictly organized to prevent circular dependencies.
- `_core.py`: Contains pure logic, Pydantic data structures, and standard `Diag` classes. No FastMCP tool definitions.
- `validate.py`: Imports `_core.py`. Exposes `@mcp.tool`.
- `graph.py`: Imports `_core.py`. Exposes `@mcp.tool`.
- `render.py`: Imports `_core.py`. Exposes `@mcp.tool`.
- `__init__.py`: Provides the unified `register_ontology_handlers(mcp: FastMCP)` method that binds the module to the server.

### Appendix U: Future Proofing with Async Processing
Currently, `fm/graph.py` is entirely synchronous. In repositories exceeding 10,000 artifacts, IO operations will begin to stall the main thread.
When porting into `ontology_check_graph_consistency`, file reads should transition to `aiofiles` to ensure the server remains responsive to simultaneous model requests.

### Appendix V: Interaction with the Context Manifest (Spec 111)
Spec 111 outlines the Context Mode manifest, enabling the AI to pull predefined contexts. The ontology tools operate strictly synergistically with this pattern.
The `ontology_query` tool can dynamically generate a path list that the agent subsequently passes into `read_files` or Context Mode buffers.
This establishes a pipeline: Query Ontology -> Generate Path Map -> Ingest Context -> Validate State.

### Appendix W: Advanced Diagnostics Parsing
When `_core.py` encounters schema mismatches, `jsonschema` outputs deeply nested and often complex error representations. The extraction MUST map these errors to human-and-agent readable strings.
For example, a missing `depends_on` array should not result in `jsonschema.exceptions.ValidationError: 'depends_on' is a required property`.
It should be formatted as:
`[SCHEMA ERROR] Line 12: Missing required L1 property 'depends_on'. Expected type: array.`
This parsing ensures the model understands exactly how to utilize `ontology_edit_frontmatter` to resolve the issue.

### Appendix X: The Role of the `return_plan` Flag
As outlined in `the-agency-system` specifications, `return_plan=True` is utilized for tools that have sweeping, multi-file side effects.
`ontology_rename_slug` changes the name of a node in the graph, which necessitates scanning all other markdown files in the repository and executing a `search-and-replace` for the old slug.
Since this touches potentially dozens of files simultaneously, it MUST be wrapped in a plan envelope. The agent executes it with `dry_run=True`, views the output, and only proceeds if confident.

### Appendix Y: Handling Malformed Subdocuments
The PR #129 documentation outlines SUBDOC placement—using Pandoc fenced divs containing YAML to describe child components.
The parser ported into `_core.py` MUST be capable of walking the markdown body and extracting these specific fenced divs.
If the agent asks `ontology_validate_frontmatter` on a file containing 4 SUBDOC components, the validator MUST return an aggregate list of diagnostics covering the root document AND all 4 child components, indicating clearly which component triggered which failure.

### Appendix Z: Cross-Domain Synergy
The overarching goal of the `agency-tooling-codemode` integration is cross-domain synergy. A music application (`bitwize-music`) and a novel generation system both rely fundamentally on directed acyclic graphs of metadata to track state. By lifting this validation into a generalized FastMCP module, the `the-agency-system` orchestrator becomes genuinely domain agnostic. It operates purely on the schema definitions provided at boot. This architecture drastically reduces the maintenance burden and prevents domain fragmentation.

## Final Note on Research Execution
This document represents an exhaustive review of the `netzkontrast/agency` tooling suite. All scripts were analyzed, dependencies mapped, and token budgets calculated. The transition pathway mapped here guarantees strict adherence to the required Code Mode integration guidelines.


### Extended Analysis: `fm/rename.py` Architecture
The script `fm/rename.py` represents the most complex procedural logic currently in the `agency` tooling suite. It performs an audited T3 operation: a cross-file slug rename.
The logic within this file performs:
1. A full scan of the frontmatter graph.
2. Identifies all instances where the target slug is referenced in `depends_on` or `affects` properties.
3. Locks the target files sequentially using `FileLock`.
4. Executes byte-level replacement to preserve surrounding text.
5. Emits detailed reports.

When extracted into `ontology_rename_slug`, this logic must be adapted to run under an asynchronous event loop without causing blocking file IO overhead. `FileLock` mechanisms must be evaluated against standard `asyncio` locking constructs, particularly when the MCP server handles multiple concurrent agent connections. The `dry_run` capability will reuse this scanning mechanism but bypass the `os.replace` step, yielding a high-confidence preview of the rename operation. This minimizes the blast radius of AI hallucinations modifying core identity parameters.

### Extended Analysis: Integration of the Auto-Repair Engine
The script `fm/fix.py` provides a mechanism for T1/T2 auto-repairs. It runs the validation suite and applies a closed-set recipe table to mechanically fix unambiguous errors (e.g., standardizing list formats or removing deprecated keys).
When ported to `ontology_fix_auto_repairs`, this tool should be classified as `deferred`. It acts as a fail-safe utility for the agent. If the agent struggles to satisfy the schema constraints manually via `ontology_edit_frontmatter`, it can trigger the auto-repair engine. The tool should return a diff of what was changed, giving the agent a learning opportunity regarding schema compliance.


### Conclusion of Porting Strategy
The strategy of porting CLI applications directly into Pydantic models solves the fundamental input typing problem in AI operations. By relying on structural validation before execution, we strip away the ambiguity of shell script arguments. The resulting `agency_mcp/handlers/ontology` module will serve as the architectural backbone of the centralized ontology mechanism.
