# Gherkin Scenarios Owned by Workflow

This document details the Gherkin scenarios from the 00-charter that the workflow column owns or co-owns.

## Owned Scenarios

These scenarios are primarily the responsibility of the `workflow` column to define and enforce.

### Scenario 3: New row plug-in
*Driven by workflow's meta-row.*
```gherkin
Given a developer adds a new row "podcast"
When they invoke the meta-row scaffolding pipeline with row name "podcast"
Then the meta-row generates the new workflow cell structures
And no base file is modified
And the central MCP picks up the new tools on next boot
And the central routing skill picks up the new skills automatically
```

### Scenario 9: Lesson-learned link-back
*Lessons are workflow artefacts produced during phases.*
```gherkin
Given a skill execution produces a lesson
When the lesson is written by the active workflow phase
Then its frontmatter cites the originating workflow phase and spec
And the graph records a lesson→spec edge
```

### Scenario 14: Column isomorphism (workflow)
*Validates the canonical shape defined in COLUMN.md.*
```gherkin
Given any two rows R1 and R2
When their workflow cells are inspected by the validation tool
Then both cells expose the canonical `manifest.toml`, `phases/`, `gates/`, and `handoffs/`
And both cells satisfy the workflow-cell schema
```

### Scenario 17: Workflow-of-creating-a-workflow (meta-row recursion)
*The core operation of META-WORKFLOW.md.*
```gherkin
Given a developer invokes the meta-row with row name "podcast"
When the meta-workflow executes its scaffold phase
Then it creates `agentic/podcast`, `workflow/podcast`, `context/podcast` from canonical templates
And all three new cells pass column-isomorphism on the first commit
```

### Scenario 18: Workflow-owned MCP tools registered in Code Mode
*Workflow declares tools; agentic registers them.*
```gherkin
Given a workflow row defines MCP tools in its agentic cell via its workflow phase definitions
When the central MCP boots
Then those tools are registered under the namespace `<row>_*`
And they are exposed in Code Mode by default
```

## Co-owned Scenarios

These scenarios represent cross-column interactions where workflow plays a vital role.

### Scenario 10: Harness-in-harness (cross-row dispatch)
*Workflows are what gets recursed into during complex operations.*
```gherkin
Given an agentic cell from row R1 dispatches into a workflow cell from row R2
When the cross-row dispatch occurs targeting a specific workflow phase
Then the dispatching handler uses the SAME four-verb contract as a leaf cell
And the workflow handoff envelope correctly traverses the row boundary
And the graph records the cross-row dispatch edge with both row identities
```

### Scenario 11: Cold-boot budget
*Workflow manifests are loaded during boot, directly affecting the budget.*
```gherkin
Given a fresh session loads the plugin
When token-usage is measured by a documented method during MCP boot
Then the `manifest.toml` of every workflow row is efficiently parsed
And the cold-boot total is below a documented numeric budget
And the budget is enforced by a CI check
```
