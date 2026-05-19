# The Context Column: Gherkin Scenarios

This document outlines the Gherkin scenarios from the charter that the `context` column owns or co-owns. It refines the `When` and `Then` steps with concrete expectations related to the context substrate.

## Owned Scenarios

### Scenario #4: Typed envelope
*The context column owns the schema definitions.*
```gherkin
Scenario: Typed envelope
  Given a tool returns a result
  When the wire payload is inspected
  Then it must successfully validate against the `tool_result.schema.json` defined in `context/_shared/schemas/`
  And it must contain at minimum the keys: ok, data, warnings, artefacts_written, next_suggested_tools, error
```

### Scenario #5: Cross-column reference via graph
*The context column provides the graph store and query mechanism.*
```gherkin
Scenario: Cross-column reference via graph
  Given a workflow cell cites a context cell in its frontmatter `related:` array
  When the graph is queried for cells `[:ADJACENT_TO]` that context node
  Then the graph query returns the workflow cell's path and metadata
  And the result is derived purely from ontology edges, without full-text search
```

### Scenario #7: Frontmatter pre-write gate
*The context column owns the schemas that enforce validation.*
```gherkin
Scenario: Frontmatter pre-write gate
  Given any cell writes a markdown file with frontmatter
  When the PreToolUse hook fires
  Then the frontmatter is schema-validated against the corresponding `<kind>.frontmatter.schema.json` from the context column
  And invalid frontmatter blocks the write operation, returning a validation error
```

### Scenario #8: Graph auto-ingest
*The context column owns the PostToolUse ingest path.*
```gherkin
Scenario: Graph auto-ingest
  Given a new frontmatter-bearing file lands in any cell
  When the PostToolUse hook fires
  Then the SQLite graph store is updated with a new node representing the file
  And the graph accurately records `CONTAINS`, `ADJACENT_TO`, and other relevant edges parsed from the frontmatter
  And no manual rebuild of the graph is required
```

### Scenario #12: Pandoc render
*The context column owns the rendering contract and templates.*
```gherkin
Scenario: Pandoc render (context column)
  Given a context cell node with frontmatter defining `render_formats` and a body
  When the user invokes `pandoc render <node>`
  Then the node is rendered to all output formats declared in its frontmatter using the designated template in `context/<row>/templates/`
  And the generated output paths are recorded in the graph with `DERIVED_FROM` edges pointing to the source node
```

### Scenario #15: Column isomorphism (context)
*The context column defines its own cell shape schema.*
```gherkin
Scenario: Column isomorphism (context)
  Given any two rows R1 and R2
  When their context cells are inspected
  Then both cells expose the canonical directory structure (README.md, manifest.toml, templates/, schemas/, references/)
  And both cells successfully validate against `context-cell.schema.json`
```

### Scenario #16: Name-driven discovery
*The context column provides the graph ontology and store enabling this.*
```gherkin
Scenario: Name-driven discovery
  Given an agent knows only a row name "music"
  When it queries the SQLite graph for the `Row` node with name "music"
  Then it can discover the row's three cells by traversing `[:CONTAINS]` edges
  And no substring search is required to locate `agentic/music`, `workflow/music`, or `context/music`
```

---

## Co-Owned Scenarios

### Scenario 13 & 14: Column isomorphism (agentic & workflow)
*Context provides the schemas (`agentic-cell.schema.json`, `workflow-cell.schema.json`) that enforce these rules, while the respective columns implement them.*

### Scenario #9: Lesson-learned link-back
*Context provides the graph ingest mechanism to record the `PRODUCED_LESSON` or `ADJACENT_TO` edge, while the workflow/agentic columns generate the lesson.*

### Scenario #17: Meta-row scaffolds via templates
*Context provides the canonical cell-shape templates located in `context/workflow/templates/` that the workflow column's pipeline uses to scaffold new rows.*
