Feature: Phase 1 — Anchor triad + envelope

  Background:
    Given the agency-mcp server is successfully booted
    And the plugin repository is loaded at the correct working directory
    And the codemode/manifest.json is accessible

  # anchor: phase-1.tools-list-payload
  Scenario: tools/list payload cold boot measurement
    When I request the list of registered tools from the MCP server
    Then the tools/list payload size must be < 4 KB

  # anchor: phase-1.boot-context-budget
  Scenario: Cold boot context token measurement
    When I measure the boot context token count via tests/smoke/test_boot_budget.py
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
    When I inspect the registration for any tool tagged with domain:shared
    Then it must be decorated with @wrap_envelope
    And the execution output must return a shared ToolResult envelope structure

  # anchor: phase-1.manifest-coverage-lint
  Scenario: Lint failure on unmanifested tools
    When a tool is registered in the server without an entry in codemode/manifest.json
    Then the manifest-coverage lint must fail the build
    And the lint output must indicate the missing tool entry

  # anchor: phase-1.cache-breakpoint-ordering
  Scenario: Prompt-cache breakpoint optimal positioning
    When I analyze the prompt structure generation
    Then the prompt-cache breakpoint must sit exactly between the anchor triad and the deferred bulk tools
