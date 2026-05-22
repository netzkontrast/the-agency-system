Feature: Phase 3 — GitHub sink wrapper
  As a system orchestrator aiming to preserve the session token budget
  I want GitHub read operations to be distilled by ephemeral subagents
  So that the main session receives a concise, typed summary under 2.5 KB

  Background:
    Given the the-agency-system repository is loaded
    And the agency-mcp server has successfully booted
    And the shared ToolResult envelope from Spec 130 is registered

  # anchor: phase-3.pr-summary-size-cap
  Scenario: gh_pr_summary returns a typed Pydantic proto under 2.5 KB for a representative 50-comment PR
    Given a representative pull request with 50 review comments and a raw pull_request_read payload exceeding 40000 tokens
    When the gh_pr_summary tool is invoked for this pull request
    Then the response must be a valid PRSummary Pydantic proto
    And the serialised JSON payload must be <= 2500 bytes
    And the response must preserve the pull request title
    And the response must preserve the CI status
    And the response must preserve requested reviewers
    And the response must preserve a body summary of <= 800 characters
    And the response must preserve severity-prefixed comments matching only [BLOCKING], [SUBSTANTIVE], or [NIT]

  # anchor: phase-3.pr-summary-small-pr
  Scenario: Calling the wrapper on a 5-comment PR returns under 1 KB
    Given a pull request with exactly 5 review comments
    When the gh_pr_summary tool is invoked for this pull request
    Then the response must be a valid PRSummary Pydantic proto
    And the serialised JSON payload must be <= 1024 bytes

  # anchor: phase-3.issue-summary-shape
  Scenario: gh_issue_summary follows the typed summary envelope shape
    Given a representative GitHub issue
    When the gh_issue_summary tool is invoked for this issue
    Then the response must be a valid IssueSummary Pydantic proto
    And the response must preserve the issue title
    And the response must preserve the CI status
    And the response must preserve requested reviewers
    And the response must preserve an issue body summary of <= 800 characters
    And the response must preserve severity-prefixed comments matching only [BLOCKING], [SUBSTANTIVE], or [NIT]

  # anchor: phase-3.review-summary-shape
  Scenario: gh_review_summary follows the typed summary envelope shape
    Given a representative GitHub pull request review with multiple comment threads
    When the gh_review_summary tool is invoked for this review
    Then the response must be a valid ReviewSummary Pydantic proto
    And the response must preserve the title
    And the response must preserve the CI status
    And the response must preserve requested reviewers
    And the response must preserve a body summary of <= 800 characters
    And the response must preserve severity-prefixed comments matching only [BLOCKING], [SUBSTANTIVE], or [NIT]

  # anchor: phase-3.main-session-never-sees-raw
  Scenario: The main session never sees the raw PR body
    Given the main session invokes a github wrapper tool
    When the wrapper executes
    Then an ephemeral subagent is spawned with a scoped tool allow-list
    And the main session does not receive the raw mcp__github__pull_request_read payload
    And the main session's tool-result for this call has byte length <= 2500

  # anchor: phase-3.subagent-tool-allow-list-read-only
  Scenario Outline: The subagent tool allow-list excludes every write/destructive GitHub tool
    Given the wrapper tool "<wrapper_tool>" is invoked
    When the wrapper executes
    Then the subagent tool allow-list must contain "<required_read_tool>"
    And the subagent tool allow-list must NOT contain any non-github tool
    And the subagent tool allow-list must NOT contain any tool whose name contains "create_", "update_", "merge_", "delete_", "push_", or ends in "_write"

    Examples:
      | wrapper_tool       | required_read_tool               |
      | gh_pr_summary      | mcp__github__pull_request_read   |
      | gh_issue_summary   | mcp__github__issue_read          |
      | gh_review_summary  | mcp__github__pull_request_read   |
