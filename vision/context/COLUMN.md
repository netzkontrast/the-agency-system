# The Context Column: Canonical Cell Shape

This document defines the canonical shape for every cell within the `context/` column of the agency matrix. The context column provides the structural and relational substrate—templates, schemas, metadata, and graph integration—that ensures the matrix rules (column isomorphism, row isomorphism, name-driven discovery) actually work.

## Cell Layout

Every cell in `context/<row>` must adhere strictly to the following directory structure. No deviations are permitted, as this layout is enforced by `context-cell.schema.json`.

```text
context/<row>/
├── README.md               # Quick-start documentation for human readability.
├── manifest.toml           # The authoritative index of the cell's contents.
├── templates/              # Pandoc/Jinja/Handlebars templates.
│   ├── <kind-1>.md.jinja   # E.g., `chapter.md.jinja` for novel.
│   └── <kind-2>.md.jinja
├── schemas/                # JSON Schema 2020-12 definitions.
│   ├── <schema-1>.json     # E.g., `character.schema.json`.
│   └── partials/           # Reusable schema fragments specific to the row.
└── references/             # Unstructured or third-party context items.
    └── <concept>.md        # Narrowly scoped reference documents.

context/_shared/            # Cross-row templates, schemas, and references.
├── schemas/                # e.g., agentic-cell.schema.json, workflow-cell.schema.json
├── templates/              # Base layouts.
└── references/             # Global rules (e.g., VOCABULARY.md).
```

## Manifest Schema

The `manifest.toml` acts as the definitive index for the cell, allowing the system to map the row without exhaustive filesystem scans.

```toml
[cell]
row = "music"
version = "1.0.0"

[ontology]
# Types this row contributes to the graph.
node_types = ["Track", "Album", "LyricSheet"]

[templates]
# Available templates and the expected context variables.
"lyric_sheet" = { path = "templates/lyric_sheet.md.jinja", inputs = ["title", "genre", "theme"] }

[schemas]
# Authoritative schemas provided by this cell.
"track_meta" = { path = "schemas/track.schema.json", type = "json-schema-2020-12" }

[search_anchors]
# Concrete discovery entry points for the anchor-triad.
"style_guidelines" = { path = "references/style.md", summary = "Style overrides and genre definitions." }
```

## Template Shape

Templates govern row isomorphism. The meta-row `workflow/workflow` uses cell-shape templates to scaffold new rows. Within a domain row, templates generate the output artefacts.

Every template must include YAML frontmatter defining rendering context and output expectations:

```jinja
---
render_formats: [md, html]
output_path: "agentic/{{ row_name }}/{{ slug }}.md"
required_vars: [title, author, summary]
---
# {{ title }}

> **Summary:** {{ summary }}

## Body
...
```

**Conventions:**
- Templates reside exclusively in `context/<row>/templates/` or `context/_shared/templates/`.
- Body content mixes static markdown and templating syntax (e.g., Jinja2).

## Schema Shape

Schemas enforce column isomorphism and valid payload structures. They must follow the JSON Schema 2020-12 specification.

**Conventions:**
- **Identifiers:** Schemas must specify an `$id` using a uniform URI scheme (e.g., `tag:agency-system.local,2026:schema:<row>/<name>`).
- **Partials:** Shared properties (e.g., standard frontmatter fields) are extracted into `schemas/partials/` and referenced via `$ref`.
- **Envelope Schemas:** The shared `ToolResult` and column cell shapes (`agentic-cell`, `workflow-cell`) are stored in `context/_shared/schemas/`.

## Reference-folder Convention

The `references/` directory holds unstructured context, third-party rules, and deep technical guidelines (the "T3 References" layer).

- **Scope:** Files here should be tightly scoped to specific concepts (e.g., `suno_prompt_guide.md`, `character_archetypes.md`).
- **Linking:** Other artefacts reference these files strictly via the graph using the `related:` frontmatter array with the reference node's slug. They are loaded progressively only on explicit demand.

## Pandoc-render Contract

A context node declares its supported output formats in its frontmatter (e.g., `render_formats: [md, pdf]`).

When a user or agent invokes `pandoc render <node>`:
1. The orchestrator reads the node's frontmatter to determine the target formats.
2. The orchestrator locates the specified template in `context/<row>/templates/`.
3. The template is populated with the node's payload and rendered to the specified output paths.
4. The newly generated output files are recorded in the graph as `SUPERSEDES` or `DERIVED_FROM` edges linking back to the original node.
