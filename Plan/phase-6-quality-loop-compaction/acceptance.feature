Feature: Phase 6 — Quality / loop / compaction
  As the agency orchestrator,
  I want durable event logging, continuous quality monitoring, loop detection, and smart compaction checkpoints,
  So that the session context is self-healing, preventing repetitive failures and saving token budgets (approx. ~47k tokens saved per loop-detected session).

  Background:
    Given the the-agency-system repository is loaded
    And the unified plugin and agency-mcp server are booted
    And the session-log MCP server at servers/session-log-mcp/ (sibling event store, not part of agency-mcp) is running
    And the orchestrator has instantiated the session event stream

  # anchor: phase-6.session-log-persistence
  Scenario: Session-log MCP persists every key event
    Given a new session is initialized
    When a PreToolUse event is emitted
    And a PostToolUse event is emitted
    And a UserPromptSubmit event is emitted
    And the same PreToolUse event is submitted twice with an identical event_id
    Then exactly one row exists for that PreToolUse event in the session-log database

  # anchor: phase-6.quality-score-computation-and-nudge
  Scenario Outline: Quality score computed on UserPromptSubmit and emits nudges
    Given the current quality score is <initial_score>
    And no nudge has been emitted in the last 5 minutes
    When a UserPromptSubmit event is processed and the new score becomes <new_score>
    Then a quality snapshot is recorded to the session-log
    And the quality score hook <action> an inline nudge in the additionalContext

    Examples:
      | initial_score | new_score | action       |
      | 85            | 65        | emits        |
      | 65            | 55        | emits        |
      | 70            | 68        | does not emit|
      | 80            | 85        | does not emit|
      | 62            | 59        | emits        |
      | 95            | 78        | emits        |

  # anchor: phase-6.quality-score-weights
  Scenario: The 7-signal quality score uses specific weights
    Given the quality score telemetry engine is initialized
    When the score.compute function aggregates the signals
    Then the weights used are exactly:
      | signal              | weight |
      | context_fill        | 0.20   |
      | stale_reads         | 0.20   |
      | bloated_results     | 0.20   |
      | compaction_depth    | 0.15   |
      | duplicates          | 0.10   |
      | decision_density    | 0.08   |
      | agent_efficiency    | 0.07   |

  # anchor: phase-6.loop-detection-triggers
  Scenario: Loop detection fires when Jaccard similarity exceeds 0.7
    Given the last 4 user messages and last 5 tool results are loaded from the session log
    And the pairwise Jaccard similarity using 3-char shingles for these items is 0.85
    When the loop detection algorithm evaluates the items
    Then a loop detection event is triggered
    And an inline nudge is emitted advising a different approach

  # anchor: phase-6.loop-notes-cooldown
  Scenario: Loop note cooldown suppresses nudges within 3 turns
    Given a session has already recorded 1 loop note
    And the last loop note was emitted 2 turns ago
    When the loop detection algorithm detects another loop
    Then no loop note is emitted due to the 3-turn cooldown

  # anchor: phase-6.loop-notes-second-emission
  Scenario: Second loop note is emitted after cooldown expires
    Given a session has already recorded 1 loop note
    And the last loop note was emitted 4 turns ago
    When the loop detection algorithm detects another loop
    Then a second loop note is emitted

  # anchor: phase-6.loop-notes-session-cap
  Scenario: Loop notes are strictly capped at 2 per session
    Given a session has already recorded 2 loop notes
    And the last loop note was emitted 5 turns ago
    When the loop detection algorithm detects another loop
    Then no loop note is emitted due to the 2-note per session cap

  # anchor: phase-6.smart-compaction-checkpoints
  Scenario: PreCompact hook snapshots and CompactionEnd restores richest checkpoint
    Given the session triggers a PreCompact event due to hitting 1 of 5 fill thresholds or 1 of 4 quality thresholds
    And there are two checkpoints available: Checkpoint A with 80% fill_pct and 1 decision, and Checkpoint B with 50% fill_pct and 9 decisions
    When the precompact_hook executes
    Then a snapshot checkpoint is taken containing the decisions, recent tool invocations, and quality score
    When a CompactionEnd event is later triggered
    Then the compaction_end_hook selects Checkpoint B as it is the richest checkpoint based on the formula
    And the hook injects a decision digest into additionalContext

  # anchor: phase-6.archive-ids-survive-compaction
  Scenario: Archive_ids written by Spec 117 survive a compaction round
    Given the session log contains tool invocations with archive_ids assigned by Spec 117
    When a PreCompact event triggers a checkpoint snapshot
    And a CompactionEnd event restores the richest checkpoint
    Then the decision digest injected into additionalContext includes the count of archived results recoverable via shared_archive_expand
    And the archive_ids are preserved in the restored checkpoint payload
