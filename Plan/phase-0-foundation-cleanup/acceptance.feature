Feature: Phase 0 — Foundation cleanup

  Background:
    Given the plugin repository is loaded as the working directory
    And the current branch is merged into Master
    And the agency-mcp FastMCP server boots successfully
    And Spec 020 and Spec 099 have been applied

  # anchor: phase-0.legacy-dir-removed
  Scenario: jules-plugin/ does not exist after the phase merges
    When the operator runs `test -d jules-plugin/`
    Then the exit code is non-zero
    And running `git ls-files jules-plugin/` returns an empty string

  # anchor: phase-0.bin-scripts-executable
  Scenario Outline: Important bin scripts live at repo root and are executable
    When the operator runs `test -x <script_path>`
    Then the exit code is 0

    Examples:
      | script_path             |
      | bin/jules-bulk          |
      | bin/jules-dev-install   |

  # anchor: phase-0.orchestrator-skill-clean
  Scenario: The orchestrator discipline skill no longer references jules-plugin
    When the operator reads `skills/agentic/jules-orchestrator-discipline/SKILL.md`
    Then the file does not contain the substring "jules-plugin/"
    And the file strictly follows the §2.2 schema frontmatter

  # anchor: phase-0.no-legacy-references
  Scenario Outline: No legacy jules-plugin references remain across the active workspace
    When the operator runs `grep -rln 'jules-plugin/' <search_path>`
    Then stdout is empty
    And the exit code is 1

    Examples:
      | search_path |
      | skills/     |
      | commands/   |
      | hooks/      |
      | docs/       |
      | CLAUDE.md   |

  # anchor: phase-0.mcp-tool-count-stable
  Scenario: The agency-mcp server still boots and maintains tool capacity
    When the operator starts the FastMCP server at `servers/agency-mcp/src/agency_mcp/server.py`
    And requests `mcp.list_tools()`
    Then the total tool count is at least 113
    And the boot context remains approximately 210 tokens

  # anchor: phase-0.pr-review-loop-converged
  Scenario: The Phase 0 PR is reviewed and converged via the JULES-REVIEW-LOOP.md mechanism
    Given a Pull Request is opened for Phase 0
    When the Gate 4 self-review is executed
    Then the orchestrator dispatches the review subagent using `Plan/_templates/review-subagent-prompt.md`
    And any issues raised are addressed and converged
    And the PR is ready to merge
