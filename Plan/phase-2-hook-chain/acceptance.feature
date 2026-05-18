Feature: Phase 2 — Hook chain
  As the token-optimizer orchestrator
  I want a chain of PreToolUse and PostToolUse hooks
  So that I can compress file reads, shell outputs, and tool results, saving 20-30% of session input and capping payloads at 4 KB

  Background:
    Given the agency-mcp server has successfully booted
    And the agency-mcp Code Mode wrapping is active
    And the hook chain is configured correctly in hooks/hooks.json

  # anchor: phase-2.pretooluse-chain-order
  Scenario: PreToolUse chain runs in the canonical order
    Given a file that triggers all PreToolUse hooks
    When the agent invokes the Read tool
    Then the PreToolUse chain MUST execute in the following exact order:
      | Order | Hook                     | Spec     |
      | 1     | contextignore_hook.py    | Spec 121 |
      | 2     | structure_map_hook.py    | Spec 115 |
      | 3     | read_cache_hook.py       | Spec 114 |
      | 4     | context_mode_sync        |          |

  # anchor: phase-2.posttooluse-chain-order
  Scenario: PostToolUse chain runs in the canonical order
    Given a large command execution that returns significant output
    When the agent invokes the Bash tool
    Then the PostToolUse chain MUST execute in the following exact order:
      | Order | Hook                     | Spec     |
      | 1     | bash_compress_hook.py    | Spec 116 |
      | 2     | context_mode_sync        |          |
      | 3     | graph_ingest             |          |
      | 4     | archive_hook.py          | Spec 117 |

  # anchor: phase-2.tool-result-archive
  Scenario: Any tool result > 4 KB is archived to disk
    Given the agent invokes a tool
    And the tool returns a payload of exactly 12000 bytes
    And the payload is archived with id "abc12345"
    When the archive_hook processes the PostToolUse event
    Then the original payload is archived to disk
    And the payload sent back to the conversation is replaced with the first 200 characters of the original
    And the payload contains the exact substring "[Full result archived (12000 chars). Use 'expand abc12345' to retrieve.]"
    And the payload size is < 4096 bytes

  # anchor: phase-2.read-cache-delta-mode-unchanged-mtime
  Scenario: Re-read of the same file with unchanged mtime returns a diff
    Given the agent Reads a 2000-line Python file at "/tmp/foo.py"
    And the file content is cached by the read-cache PostToolUse hook
    And the agent edits "/tmp/foo.py" changing exactly 1 line without altering the file's mtime
    When the agent Reads "/tmp/foo.py" a second time with the exact same mtime
    Then the read_cache_hook emits additionalContext of kind="delta"
    And the body returned is a unified diff
    And the byte length of the diff is ≤ 10% of the file's full byte length

  # anchor: phase-2.read-cache-delta-mode-changed-mtime
  Scenario: Re-read of the same file with changed mtime behaves as fresh read
    Given the agent Reads a 2000-line Python file at "/tmp/foo.py"
    And the file content is cached by the read-cache PostToolUse hook
    And the agent edits "/tmp/foo.py" changing exactly 1 line and the file's mtime advances
    When the agent Reads "/tmp/foo.py" a second time
    Then the read-cache hook lookup misses on mtime mismatch
    And the next PostToolUse repopulates the cache with the new content

  # anchor: phase-2.structure-map-ast-python
  Scenario Outline: Massive code files return an AST skeleton instead of the full body
    Given a file at "<filepath>" with <lines> lines and <size> bytes
    When the agent invokes the Read tool on "<filepath>"
    Then the structure_map_hook emits additionalContext of kind="structure_map"
    And the returned text contains an AST skeleton
    And the Read call is bypassed so the body is not sent to the cache hook or model

    Examples:
      | filepath       | lines | size     |
      | /tmp/huge.py   | 25000 | 900000   |
      | /tmp/large.py  | 1000  | 850000   |
      | /tmp/long.py   | 21000 | 400000   |

  # anchor: phase-2.structure-map-ast-python-bypass
  Scenario: Files below both thresholds bypass the AST hook
    Given a file at "/tmp/small.py" with 1000 lines and 50000 bytes
    When the agent invokes the Read tool on "/tmp/small.py"
    Then the structure_map_hook exits 0 with no stdout
    And the downstream read_cache_hook handles the call

  # anchor: phase-2.contextignore-hard-block
  Scenario: .contextignore hard-blocks Read, Glob, and Grep tools before any cache fires
    Given a project root with a ".contextignore" file containing "secrets/**"
    And a global "~/.claude/.contextignore" file containing "*.pem"
    When the agent invokes the Read tool on "secrets/api.key"
    Then the contextignore_hook blocks the call with action="block"
    And the read_cache_hook is never invoked for this file
    When the agent invokes the Read tool on "server.pem"
    Then the contextignore_hook blocks the call via the global rule

  # anchor: phase-2.bash-compress-credentials
  Scenario: Credential-pattern preservation in bash compression
    Given the agent invokes Bash with a command that outputs 1000 lines
    And one of the lines contains the token "ghp_AbCdEf1234567890mnopqrstuvwxyz"
    When the bash_compress_hook processes the PostToolUse event
    Then the total output length is significantly reduced
    And the exact token "ghp_AbCdEf1234567890mnopqrstuvwxyz" MUST be preserved verbatim in the compressed output
