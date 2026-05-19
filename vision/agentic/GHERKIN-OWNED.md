# Owned Gherkin Scenarios: agentic column

This document refines the Gherkin scenarios owned or co-owned by the `agentic` column (from `00-charter.md`). It provides concrete expectations for assertions and expected state changes.

## Scenario 1: Session-start routing (OWN)
```gherkin
  Scenario: Session-start routing
    Given a fresh Claude Code session
    When the session loads the agency-system plugin
    Then a routing surface is available within the documented cold-load budget (< 500 tokens)
    And the routing surface explains the workflow rows currently registered (e.g., music, novel, jules)
```
**Refinement:** The "routing surface" is the `agentic/_router/SKILL.md` (the `/agency` command). It must load without initializing heavy workflow state, strictly pulling from `manifest.toml` summaries.

## Scenario 2: What-next query (OWN)
```gherkin
  Scenario: What-next query
    Given the user asks "what should I do next?"
    When the routing surface processes the intent
    Then candidates are returned ranked by graph adjacency, not substring match
    And the returned candidate is a skill slug defined in an `agentic/<row>/manifest.toml`
```
**Refinement:** The central routing skill queries the `context` graph, identifying the most probable `agentic/<row>/skills/<slug>` to hand off to based on recent user actions.

## Scenario 6: Code-mode delegation (OWN)
```gherkin
  Scenario: Code-mode delegation
    Given a skill frontmatter declares `prefers_codemode: true`
    When the skill is dispatched
    Then the central MCP renders the skill's call surface in Code Mode
    And the tool list implicitly includes `search` and `execute`
    And an envelope-archive interceptor applies inside the sandbox, capping payload to 4 KB
```
**Refinement:** FastMCP code_mode transforms are wired exclusively when the agentic cell's frontmatter sets this flag. Handlers must output `ToolResult` envelopes that the interceptor truncates if they exceed budget.

## Scenario 10: Harness-in-harness (OWN)
```gherkin
  Scenario: Harness-in-harness (cross-row dispatch)
    Given an agentic cell from row "music" dispatches into a workflow cell from row "novel"
    When the `dispatch_skill` tool is called
    Then the dispatching handler uses the SAME four-verb contract as a leaf cell
    And the graph records the cross-row `DispatchedTo` edge with both row identities ("music" -> "novel")
    And the payload strictly conforms to `{"row": "novel", "phase": "...", "context_refs": [...]}`
```
**Refinement:** Cross-row dispatch is an agentic primitive. It must use standard MCP payload structures.

## Scenario 13: Column isomorphism - agentic (OWN)
```gherkin
  Scenario: Column isomorphism (agentic)
    Given any two rows R1 and R2
    When their agentic cells are inspected
    Then both cells expose `manifest.toml`, `handlers/`, and `skills/`
    And both cells satisfy the `agentic-cell.schema.json` defined in the context column
```
**Refinement:** Handlers are strictly in `handlers/`, skills strictly in `skills/`, and no rogue directories exist. Tools are namespaced strictly as `<row>_*`.

## Scenario 17: Workflow-owned MCP tools (OWN)
```gherkin
  Scenario: Workflow-owned MCP tools registered in Code Mode
    Given a workflow row defines MCP tools in its agentic cell
    When the central MCP boots
    Then those tools are registered under the namespace `<row>_*`
    And they are exposed in Code Mode by default if the skill prefers it
```
**Refinement:** Bootstrapper script reads the `[tools] exports` from the `agentic/<row>/manifest.toml` and applies `@mcp.tool` namespaces programmatically.

## Scenario 3: New row plug-in (CO-OWN with workflow)
```gherkin
  Scenario: New row plug-in
    Given a developer adds a new row "podcast"
    When they create the three cells from canonical templates
    Then no base file is modified
    And the central MCP reads `agentic/podcast/manifest.toml` and picks up new tools on next boot
    And the central routing skill picks up the new skills automatically via graph ingestion
```
**Refinement (agentic):** The bootloader dynamically globs `agentic/*/manifest.toml`.

## Scenario 11: Cold-boot budget (CO-OWN with context)
```gherkin
  Scenario: Cold-boot budget
    Given a fresh session loads the plugin
    When token-usage is measured by a documented method
    Then the cold-boot total is below a documented numeric budget (< 500 tokens)
    And the budget is enforced by a CI check
```
**Refinement (agentic):** The agentic cell must use `defer_schema=True` for its tools during FastMCP registration to keep the `tools/list` payload under 4 KB.
