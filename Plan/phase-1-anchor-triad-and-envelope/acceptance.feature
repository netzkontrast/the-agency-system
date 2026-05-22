Feature: Phase 1 — Anchor triad + envelope (cold-start)

  Background:
    Given the agency-mcp server is successfully booted
    And the plugin repository is loaded at the correct working directory
    And the servers/agency-mcp/src/agency_mcp/codemode/manifest.json is accessible
    And the L1 in-process harness from PR #127 is present at tests/_harness/

  # anchor: phase-1.tools-list-payload
  Scenario: tools/list payload cold boot measurement
    When I run tests/smoke/test_boot_budget.py via the L1 harness's harness_mcp() factory and request the list of registered tools from the MCP server
    Then the tools/list payload size must be < 4 KB

  # anchor: phase-1.boot-context-budget
  Scenario: Cold boot context token measurement
    When I measure the boot context token count via tests/smoke/test_boot_budget.py invoked through the L1 harness's harness_mcp() factory
    Then the total boot context token count must be < 500 tokens

  # anchor: phase-1.eager-anchor-registration
  Scenario Outline: Eager registration of the anchor triad
    When I inspect the list of eager tools in the MCP registry
    Then the tool "<tool_name>" must be registered with hidden=False
    And the tool "<tool_name>" must not have defer_schema=True

    Examples:
      | tool_name            |
      | agency_tool_search   |
      | agency_tool_describe |
      | agency_tool_invoke   |

  # anchor: phase-1.deferred-bulk-registration
  Scenario: Deferred registration for non-anchor tools
    When I retrieve the configuration for all non-anchor domain tools
    Then every other domain tool must be registered with hidden=True
    And every other domain tool must have defer_schema=True

  # anchor: phase-1.shared-envelope-enforcement
  Scenario: The @wrap_envelope decorator on shared tools
    When I iterate the registration of every tool tagged with domain:shared
    Then each MUST be decorated with @wrap_envelope
    And the execution output must return a shared ToolResult envelope structure

  # anchor: phase-1.manifest-coverage-lint
  Scenario: Lint failure on unmanifested tools
    When a tool is registered in the server without an entry in codemode/manifest.json
    Then the manifest-coverage lint must fail the build
    And the lint output must indicate the missing tool entry

  # anchor: phase-1.cache-breakpoint-ordering
  Scenario: Prompt-cache breakpoint optimal positioning
    When I read codemode/manifest.json
    Then the entry with kind="cache_breakpoint" sits at an index strictly greater than the last triad tool and strictly less than the first deferred bulk tool

  # anchor: phase-1.toon-gate
  Scenario: TOON serializer size reduction gate
    When I run tests/smoke/test_toon_gate.py via the L1 harness's harness_mcp() factory with a homogeneous list of dicts of length >= 3
    Then the serialized payload size must demonstrate a 40-60% reduction over raw JSON