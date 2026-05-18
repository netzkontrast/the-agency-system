---
spec_id: 123
slug: agency-tooling-codemode
status: draft
owner: jules
depends_on: [008, 111, 122]
affects:
  - servers/agency-mcp/src/agency_mcp/handlers/ontology/
  - servers/agency-mcp/src/agency_mcp/handlers/ontology/__init__.py
  - codemode/manifest.json
  - hooks/hooks.json
source-repos: [netzkontrast/agency @ main]
estimated_jules_sessions: 2
domain: cross
wave: D
---

# Spec 123: Agency Tooling Extraction + MCP Code Mode Integration

## Why

Brief 1 (Spec 122) established a centralized ontology data shape (types, schemas, edges, modes). However, a data shape is inert without machinery to enforce it. The `netzkontrast/agency` repository contains a mature suite of Python validation, linting, rendering, and auditing tools (`tools/fm/`, `check-*.py`).

By extracting these tools and wrapping them as FastMCP Code Mode tools (Spec 008) and `PostToolUse` hooks within `the-agency-system`, we give the model native, programatic access to the ontology. Skills can validate pre-commit invariants, hooks become deterministic via unified schemas, and graph-aware queries can resolve complex context dependencies efficiently.

## Done When

- The agency `fm` tooling and relevant `check-*.py` scripts MUST be ported to `agency_mcp/handlers/ontology/`.
- Four eager anchor tools (`ontology_validate_frontmatter`, `ontology_check_graph_consistency`, `ontology_render_readme`, `ontology_query`) MUST be registered and documented.
- The `codemode/manifest.json` MUST map these tools accurately with `eager`, `deferred`, or `background` classifications.
- A centralized `hooks/validate_ontology.py` MUST be registered in `hooks/hooks.json` to fire PostToolUse on edits to Markdown files with frontmatter.
- Tool responses MUST adhere to the token efficiency policy, returning summaries by default.
- Stateful tools MUST support `dry_run=True` and return the `{would_apply, diff, warnings}` envelope.

## Source clones

```bash
git clone --depth=1 --branch=main https://github.com/netzkontrast/agency.git ~/work/vendor/agency
cd ~/work/vendor/agency && git fetch origin pull/129/head:pr-129
```

## Files

**Create:**
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/__init__.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/validate.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/graph.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/render.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/query.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/edit.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/govern.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/rename.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/fix.py`
- `servers/agency-mcp/src/agency_mcp/handlers/ontology/_core.py`
- `hooks/validate_ontology.py`

**Modify:**
- `codemode/manifest.json`
- `hooks/hooks.json`

## Approach

### Gate 1: Confidence & Design

The `netzkontrast/agency` tools are standalone Python files that rely heavily on `argparse` for inputs. We will extract the CLI argument parsing and replace it with strongly typed Pydantic models conforming to the FastMCP `@mcp.tool()` signature requirement. Tool docstrings MUST be strictly ≤ 120 characters and imperative to comply with overview §2.1. Tool names MUST follow the snake_case `ontology_<verb>_<object>` convention.

### Gate 2: TDD / Red-Green-Refactor

Write pytest cases against `servers/agency-mcp/src/agency_mcp/handlers/ontology/` verifying the core behavior independent of the MCP server:
1. Valid frontmatter correctly parses and passes.
2. Invalid frontmatter fails and produces structured `Diagnostic` outputs.
3. Graph cyclic dependencies are accurately detected.
4. `dry_run=True` mutates zero bytes on disk and correctly computes diffs.

### Gate 3: Evidence

Provide pytest stdout output and MCP local tool invocation payloads proving the anchor tools return correct shapes under the required token budget. Provide screenshot or logs of the `PostToolUse` hook successfully catching an edit.

### Gate 4: Self-Review

Verify `return_plan` usage, ensure the correct tag namespaces are utilized (`domain:agentic`, `kind:ontology`, `anchor_kind:eager`), and confirm hook timing constraints are satisfied. Document explicitly if any structural logic deviates from the PR #129 specification.

## Acceptance

**Scenario 1: Frontmatter validation on a representative file**
Given a `task.md` with missing required frontmatter fields,
When `ontology_validate_frontmatter("task.md")` is called,
Then the tool MUST return an ERROR diagnostic citing the schema violation.

**Scenario 2: Graph-consistency check detects a broken edge**
Given a spec artifact with a `depends_on` edge pointing to a non-existent slug,
When `ontology_check_graph_consistency()` is called,
Then the tool MUST emit a dangling reference warning.

**Scenario 3: Readme auto-render is byte-identical**
Given a complete set of frontmatter inputs,
When `ontology_render_readme(path)` is run twice consecutively,
Then the second run MUST yield a byte-identical markdown output to the first, with no source changes.

**Scenario 4: Code Mode boot token budget**
When the `ontology` namespace is booted,
Then the 4 eager anchor tools MUST contribute less than 315 total tokens (≤ 5% overhead) to the context prompt.

**Scenario 5: PostToolUse hook timing**
When a `Write` tool modifies a Markdown file containing frontmatter,
Then the `PostToolUse` hook running `validate_ontology.py` MUST fire and complete within 500 ms.

**Scenario 6: `dry_run=True` behavior**
Given a valid `ontology_edit_frontmatter` command with `dry_run=True`,
When the tool is invoked,
Then it MUST return a `{would_apply, diff, warnings}` dictionary AND the underlying file MUST NOT be mutated.

## Out of Scope

- Integrating agency-specific strict governance rules (e.g., `check-canon-status.py`, `check-rfc2119-polarity.py`) that do not apply to the broader plugin domain.
- Designing the inner details of music/novel domain validators (Spec 017 territory). The single generalized `validate_ontology.py` is the only hook this spec concerns itself with.

## References

- [Spec 111: Context Mode Manifest](../111-context-mode-manifest/spec.md)
- [Spec 008: Code Mode Registry](../008-codemode-registry/spec.md)
- netzkontrast/agency `tools/fm/`
- netzkontrast/agency `check-*.py`
