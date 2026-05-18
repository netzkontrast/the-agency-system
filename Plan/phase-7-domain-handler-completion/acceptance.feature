Feature: Phase 7 — Domain handler completion

  Background:
    Given the agency-mcp server has successfully booted
    And the plugin repository the-agency-system is loaded
    And Spec 014 (novel-gates-and-revision) has been merged via PR #108
    And the current branch is Master
    And the total boot context token usage is below 500 tokens

  # anchor: phase-7.novel-skills-catalogue
  Scenario: Novel skills catalogue contains 28 spirit-isomorphic skills
    Given the novel domain directory skills/novel/ exists
    When I count the number of skills defined in the novel domain
    Then exactly 28 SKILL.md files exist under skills/novel/ that are NOT under skills/novel/prompts/
    And the skill novel-work-conceptualizer exists
    And the skill novel-chapter-writer exists

  # anchor: phase-7.agentic-handlers-registration
  Scenario: Agentic handlers correctly register 32 tools
    Given the agentic handlers are defined under servers/agency-mcp/src/agency_mcp/handlers/agentic/
    When I inspect the FastMCP registered tools tagged with domain:agentic
    Then exactly 32 tools are registered in the agentic domain
    And the prefixes agentic_spec_*, agentic_plan_*, agentic_workflow_*, agentic_research_*, agentic_ralph_*, and agentic_confidence_* are non-empty
    And the tools/list payload is under 4 KB

  # anchor: phase-7.overrides-migration
  Scenario: Overrides migration separates global preferences from project data
    Given the overrides/ directory exists at the repository root
    When I list the contents of the overrides/ directory
    Then it contains cross-project preference files including prose-style-guide.md, narrative-preferences.md, dramatica-defaults.md, and ncp-defaults.md
    But no album-specific content or project-specific content exists in the overrides/ directory

  # anchor: phase-7.novel-prompt-builders
  Scenario: Novel prompt builders are implemented as 10 specialized skills
    Given the novel prompt builder feature is implemented
    When I check the skills/novel/prompts/ directory
    Then exactly 10 prompt builder SKILL.md files are present
    And skills for scene, character, world, throughline, and bridge prompt builders exist

  # anchor: phase-7.shared-toolresult-envelope
  Scenario Outline: Every domain handler tool returns the shared ToolResult envelope
    Given the FastMCP tool <tool_name> is invoked
    When the tool execution completes
    Then the response shape strictly conforms to the shared ToolResult envelope from Spec 130
    And the response contains the keys ok, data, warnings, artefacts_written, and next_suggested_tools

    Examples:
      | tool_name |
      | novel_create_work |
      | music_list_albums |
      | agentic_validate_confidence |
      | novel_scene_prompt_builder |

  # anchor: phase-7.skill-tool-hooks-validation
  Scenario: Skill-tool hooks verify Skill|Agent matchers resolve correctly
    Given the skill-tool-hooks from Spec 132 are active
    When a tool matching the Skill|Agent pattern is executed
    Then the pre/post hook script runs
    And the script successfully validates that the provided skill slug resolves to a real skill on disk

  # anchor: phase-7.no-orphaned-handlers
  Scenario: No orphaned handlers exist across any domain
    Given all tools are registered in the agency-mcp server
    When I parse the agency-mcp tool registry and grep skills/, commands/, hooks/ for each tool name
    Then every registered handler appears as a caller in at least one of those three trees
