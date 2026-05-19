Feature: Phase 4 — Context Mode Path B
  As an AI agent operating the agency-system
  I want a deferred-loading context manifest (Context Mode Path B)
  So that the boot token budget stays under 500 tokens while allowing structured search over >= 200 KB of documents

  # Naming note: "Context Mode Path B" (this phase) is distinct from
  # "Harness Path B" (the structural-restructure trajectory in
  # Plan/harness/design.md §11). See Plan/harness/VOCABULARY.md §6.

  Background:
    Given the agency-system repository is checked out and clean
    And the FastMCP agency-mcp server is installed
    And PR #104 (Spec 112: context-anchor-triad) is merged and its tools are active
    And PR #113 (Spec 113: context-cache-and-subscriptions) is merged and active

  # anchor: phase-4.manifest-builder-determinism
  Scenario: Manifest builder produces a deterministic JSON catalogue
    Given the corpus of spec, lesson, override, and reference files exists
    When the operator runs "python bin/build_context_manifest.py --root . --out servers/agency-mcp/src/agency_mcp/codemode/context_manifest.json"
    Then the process exits with status 0
    And the generated JSON file contains an array of context entries
    And running the command a second time produces a byte-identical JSON file

  # anchor: phase-4.manifest-entry-schema
  Scenario Outline: Each manifest entry conforms to the required schema and taxonomy
    Given the generated "servers/agency-mcp/src/agency_mcp/codemode/context_manifest.json"
    When I inspect the entry for <file_type>
    Then it has the fields "id", "title", "summary", "sha256", "tags", "mime", "path", "views", and "graph_id"
    # Note: "graph_id" is the bridge field shared with Phase 5 (Wave D ontology graph).
    And the "views" object contains "summary", "preview", and "full"
    And all tags begin with one of the allowed prefixes: "domain:", "kind:", "topic:", "spec:", "slug:"

    Examples:
      | file_type       |
      | a Spec file     |
      | a Lesson file   |
      | an Override     |
      | a Reference doc |

  # anchor: phase-4.anchor-triad-integration
  Scenario: The context_anchor_triad consults the populated manifest
    Given the manifest is populated in "servers/agency-mcp/src/agency_mcp/codemode/context_manifest.json"
    When I call the "context_search" tool with query "dramatica"
    Then the tool returns a list of ranked hits from the manifest
    And the highest-ranked hit is tagged "topic:dramatica"

  # anchor: phase-4.cache-and-subscriptions
  Scenario: Cache and subscriptions emit notifications on manifest change
    Given an active MCP client is subscribed to context resources via "notifications/resources/updated"
    When the manifest file's mtime or sha256 is modified
    Then the server emits a "notifications/resources/updated" notification to the client

  # anchor: phase-4.108-supersession
  Scenario: Spec 108-stub points to Context Mode Path B
    Given the file "Plan/108-context-mode-integration/spec.md" exists
    When I read its contents
    Then it contains a one-line supersession note pointing to specs 111, 112, and 113

  # anchor: phase-4.baseline-token-budget
  Scenario: Cold session boot keeps token budget under 500 tokens
    Given a cold session boot of the agency-mcp server
    When no "context_read" tool has been explicitly called
    Then zero spec, lesson, or override files are read into memory
    And the boot context size remains under 500 tokens
