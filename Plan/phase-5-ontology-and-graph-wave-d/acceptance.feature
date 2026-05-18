Feature: Phase 5 — Ontology + Graph (Wave D)
  In order to execute cross-domain queries efficiently and validate artefacts systematically
  As an orchestrating agent or developer
  I want the agency system to provide a unified semantic ontology, a local EAV graph cache, and enforceable traceability lints

  Background:
    Given the the-agency-system repository is loaded and the master branch is checked out
    And the agency-mcp FastMCP server boots successfully
    And the shared StateCache and base configurations are active

  # anchor: phase-5.ontology-types
  Scenario: header-ontology.json declares 18 artefact types with typed edges and cardinality
    Given the centralized L1 schema is active
    When the schema parser loads "maintenance/schemas/header-ontology.json"
    Then the schema MUST declare exactly 18 distinct artefact types covering music, novel, and agentic domains
    And each type MUST define its allowable incoming and outgoing edges
    And each edge MUST explicitly define cardinality constraints (e.g. one-to-many, one-to-one)

  # anchor: phase-5.agency-tooling-eager-anchors
  Scenario: ontology anchors are registered eagerly within token budget
    Given the Code Mode tool registry is queried
    When the "ontology" namespace tools are registered
    Then tools "ontology_validate_frontmatter", "ontology_check_graph_consistency", "ontology_render_readme", and "ontology_query" MUST be registered as eager anchors
    And their combined token payload in the tool context MUST be ≤ 170 tokens
    And the "tools/list" overall payload MUST remain < 4 KB

  # anchor: phase-5.graph-eager-anchors
  Scenario: graph tools are available and operate over the local sqlite cache
    Given the graph component is enabled
    When the "tools/list" request is executed
    Then tools "graph_cypher", "graph_describe_node", and "graph_run_algorithm" MUST be present as eager anchors
    And these tools MUST read from and write to "~/.agency-system/cache/graph.sqlite"

  # anchor: phase-5.fast-cypher-match
  Scenario: A Cypher MATCH for spec->spec dependencies is fast
    Given the local graph.sqlite is populated with spec dependencies
    When "graph_cypher" is executed with a MATCH query looking for dependency paths between specs
    Then the result set MUST be returned in < 100 ms

  # anchor: phase-5.agnostic-ingest
  Scenario: PostToolUse hook and watcher append to graph_pending_writes for incremental ingest
    Given a Markdown artefact file is modified on disk
    When the Claude Code "Write" tool completes OR a background process edits the file directly
    Then both the synchronous PostToolUse hook and the Spec 113 filesystem watcher MUST fire
    And both mechanisms MUST append the modified file path to "graph_pending_writes.json"
    And the graph cache MUST be updated incrementally

  # anchor: phase-5.traceability-lint
  Scenario: spec-test anchor traceability lint passes
    Given the test traceability lint is executed via "python Plan/_lint/check_anchor_coverage.py"
    When the linter scans the repository for Gherkin scenario tags
    Then the linter MUST exit with status 0
    And every "# anchor: NNN.n" Gherkin tag MUST map to at least one pytest case under "tests/"

  # anchor: phase-5.pagerank-execution
  Scenario: PageRank over the spec graph runs end-to-end without external services
    Given the GraphQLite core is initialized with in-process EAV data
    When "graph_run_algorithm" is called with "pagerank" over the "spec" domain
    Then the algorithm MUST complete successfully using the built-in C extension
    And the sum of the returned PageRank scores MUST be ≈ 1.0
    And no external network calls or database servers MUST be involved

  # anchor: phase-5.type-validation-outline
  Scenario Outline: Frontmatter schema validation for specific domains
    Given an artefact file of type "<type>" exists
    When "ontology_validate_frontmatter" is run against the artefact
    Then the validator MUST enforce rules specific to the "<domain>" domain

    Examples:
      | type     | domain  |
      | track    | music   |
      | chapter  | novel   |
      | research | agentic |
      | spec     | shared  |