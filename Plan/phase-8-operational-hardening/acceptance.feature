Feature: Phase 8 — Operational hardening
  As a maintainer of the agency-system unified plugin
  I want robust operational guardrails, composable watchers, and harness parity tests
  So that the plugin stays reliable and portable (polish + bus-factor + cross-harness portability)

  Background:
    Given the "agency-system" repository is loaded as a FastMCP plugin
    And the plugin boot context is under 500 tokens
    And the current branch is "Master"
    # Canonical naming for the layers and verbs referenced below lives in
    # Plan/harness/VOCABULARY.md; the L3 daemon implementation under this
    # phase is specified in Plan/harness/design.md §5 (its acceptance
    # scenarios live in Plan/harness/design.md §8 as harness.L3.1..L3.5).

  # anchor: phase-8.pr-rebase-policy
  Scenario: PR-rebase policy is enforced via a CI gate
    Given a PR branch "feature/test-branch" is created
    And the CI gate reads N days from ".github/workflows/rebase-policy.yml"
    And the base commit of "feature/test-branch" is older than N days compared to the "Master" branch HEAD
    When the CI pipeline executes the PR validation checks
    Then the CI pipeline fails with a message indicating the base commit is more than N days stale
    And the pipeline prompts the author to rebase against "Master"

  # anchor: phase-8.pressure-tests
  Scenario Outline: Skill-subagent pressure tests pass for all skills
    Given the agency toolkit has ~140 registered skills
    When the pressure test suite runs against the "<skill_kind>" skill cluster using fixture "<fixture_path>"
    Then the test suite executes without unhandled exceptions
    And all skills in the cluster gracefully recover from invalid inputs

    Examples:
      | skill_kind     | fixture_path                                 |
      | discipline     | tests/fixtures/pressure_discipline.json      |
      | orchestrator   | tests/fixtures/pressure_orchestrator.json    |
      | domain         | tests/fixtures/pressure_domain.json          |
      | workflow       | tests/fixtures/pressure_workflow.json        |

  # anchor: phase-8.agents-manifest
  Scenario: agents.yaml at repo root manifests every role with handoff registry
    Given the "agents.yaml" manifest exists at the repository root
    When the manifest is parsed by the discovery service
    Then every active role is manifested in the handoff registry
    And the "lint_agents_schema.py" script passes without errors
    And the "lint_agents_orphans.py" script passes without errors
    And the tools "agents_list", "agents_describe", and "agents_handoff_graph" return the exact agent graph specified in the manifest

  # anchor: phase-8.frustration-log-protocol
  Scenario: Frustration-log protocol mandates entries per PR
    Given a PR is ready for submission
    When the pre-commit frustration-log hook executes
    Then it verifies the PR description contains a valid FL0-FL3 frustration log entry
    And if no frustration occurred, it verifies the explicit null-baseline declaration is present

  # anchor: phase-8.evidence-snapshot
  Scenario: Evidence-snapshot helper auto-captures artefacts into Gate 3 blocks
    Given a clean install environment test run has completed
    When the "evidence-snapshot" helper is invoked
    Then it captures the pytest JUnit XML report
    And it captures the ruff/pyflakes log
    And it captures the clean-install transcript
    And it formats the combined artefacts into a valid Markdown Gate 3 Evidence block suitable for the PR body

  # anchor: phase-8.harness-research-doc
  # Note: this scenario covers the Spec 023 *research-remainder* only
  # (items 1 = prior-art survey + 4 = progressive-disclosure ladder).
  # The L3 daemon implementation that absorbed Spec 023 items
  # 2-3-5-6-7-8-basic has its own acceptance scenarios in
  # Plan/harness/design.md §8 (harness.L3.1 through harness.L3.5).
  Scenario: Harness-in-harness research epic produces the compatibility enumeration doc
    Given the harness-in-harness research epic script is executed
    When the findings are aggregated
    Then the document path matches "Plan/_session-state/\d{4}-\d{2}-\d{2}-jules-research-\d+-harness\.md"
    And the document enumerates which plugin surfaces function correctly in bash-only and non-MCP harnesses
    And the document enumerates any MCP-exclusive surfaces

  # anchor: phase-8.watcher-composability-webhook
  Scenario: Watcher SDK composability multiplexes Jules and GitHub PR sources via webhooks
    Given the "CompositeWatcher" driver is initialized
    When it polls for events
    Then it successfully receives events from the Jules REST API
    And it successfully receives events from GitHub PR webhooks
    And it normalizes all received events behind a single "Protocol" interface

  # anchor: phase-8.watcher-composability-polling
  Scenario: Watcher SDK composability multiplexes Jules and GitHub PR sources via polling
    Given the "CompositeWatcher" driver is initialized
    When it polls for events
    Then it successfully receives events from the Jules REST API
    And it successfully receives events from GitHub PR polling endpoints
    And it normalizes all received events behind a single "Protocol" interface
