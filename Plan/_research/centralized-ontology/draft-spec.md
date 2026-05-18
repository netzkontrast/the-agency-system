---
spec_id: 122
slug: centralized-ontology
status: draft
owner: jules
depends_on: [111, 112, 113]
affects: ["maintenance/schemas/l1-vault-core.schema.json", "maintenance/schemas/header-ontology.json", "maintenance/schemas/l2-readme.schema.json", "tools/fm/validate.py", "tools/cli/agency_ontology.py", "templates/readme.j2"]
domain: cross
wave: D
---

# Spec 122: Centralized Ontology for Plugin Domains

## Why

The `the-agency-system` plugin currently suffers from ad-hoc, localized conventions across its domains (music, novel, jules, agentic). This fragmentation prevents cross-domain querying, complicates validation, and limits the richness of the Context Mode Path B architecture. By adopting a centralized ontology—inspired by `netzkontrast/agency` PR #129 but adapted for our specific domains—we unify metadata, explicitize edge relationships, and unlock automated documentation generation.

## Done When

1. **L1 Vault Core Schema**: `l1-vault-core.schema.json` is defined, supporting an extended enum of types (`task`, `prompt`, `research`, `spec`, `readme`, `note`, `skill`, `adr`, `track`, `album`, `work`, `chapter`, `override`, `lesson`, `reference`, `ontology-entry`, `prompt-builder`, `gherkin`).
2. **Edge Declarations**: `header-ontology.json` is created, defining explicit edge keys, cardinality, and source/target constraints.
3. **Linter Update**: `tools/fm/validate.py` is updated to enforce the new L1 schema across all tracked markdown files.
4. **Auto-Readme Contract**: `l2-readme.schema.json` and a Jinja2 template (`templates/readme.j2`) are implemented to generate readmes from artifact frontmatter.
5. **CLI Tooling**: `tools/cli/agency_ontology.py` is implemented with `lint` and `readme` subcommands.

## Source clones

None required for implementation. All necessary research was completed during the `centralized-ontology` brief phase.

## Files

- **Create**: `maintenance/schemas/l1-vault-core.schema.json`
- **Create**: `maintenance/schemas/header-ontology.json`
- **Create**: `maintenance/schemas/l2-readme.schema.json`
- **Create**: `templates/readme.j2`
- **Create**: `tools/cli/agency_ontology.py`
- **Modify**: `tools/fm/validate.py`

## Approach

1. **Gate 1 - Confidence**: The centralized ontology concept is fully researched (see `Plan/_research/centralized-ontology/findings.md`). The schemas MUST strictly adhere to JSON Schema Draft 07. The Jinja2 templates MUST gracefully handle missing optional fields.
2. **Gate 2 - TDD**: Write tests for the `agency_ontology.py` CLI and `validate.py` linter before implementation. Ensure RED -> GREEN -> REFACTOR.
3. **Schema Definition**: Author the L1 schema and the ontology header. Ensure the type enum covers all domains.
4. **Tooling Implementation**: Implement the `validate.py` updates to parse frontmatter and apply the schemas. Implement the `agency_ontology.py` CLI to drive the Jinja2 readme generation.
5. **Gate 3 - Evidence**: Provide stdout of passing tests and successful linting runs.
6. **Gate 4 - Self-Review**: Verify that no out-of-scope files were modified and that the schema correctly validates a representative sample of artifacts.

## Acceptance (Gherkin)

```gherkin
# anchor: 122.1
Scenario: L1 schema validates a representative sample from each domain
  Given the centralized L1 schema is active
  When the linter evaluates a valid spec, track, and skill file
  Then the validation succeeds without errors

# anchor: 122.2
Scenario: Edge linter detects a broken edge
  Given an artifact defines a "spec_depends_on" edge
  And the target of that edge does not exist
  When the ontology linter runs
  Then it MUST fail with an error detailing the broken edge

# anchor: 122.3
Scenario: Auto-readme renderer is byte-identical on second run
  Given a valid artifact file
  When the readme generator runs
  And it runs a second time
  Then the output MUST be byte-identical

# anchor: 122.4
Scenario: A missing required L2 field fails CI
  Given a track artifact missing the required "track_bpm" L2 field
  When the linter evaluates the file
  Then it MUST fail validation with a specific L2 error

# anchor: 122.5
Scenario: Path B context_search returns ontology-typed results
  Given the context manifest is built with the new ontology
  When context_search is queried
  Then the returned entries MUST include the correct ontology "type" tag
```

## Out of scope

- Full migration of all existing files to the new schemas. This spec only builds the foundation and tooling. The migration will occur incrementally in subsequent specs.
- Modifying the fastMCP server internals. The Context Mode handlers will consume the generated manifest, but the server code itself is not modified here.

## References

- `Plan/JULES_PROTOCOL.md`
- `Plan/111-context-mode-manifest/spec.md`
- `netzkontrast/agency` PR #129 (Migration locks L11.32‴, L11.36′, L11.44)
