---
slug: vision-four-verb-canon
type: spec
status: ready
owner: claude
created: 2026-05-20
updated: 2026-05-20
summary: The four-verb contract (mcp__list_tools, mcp__call_tool, mcp__list_skills, mcp__dispatch_skill) extracted as top-level canon. Names the verbs, fixes the namespacing (mcp__ prefix required), references the wire-level schemas at vision/specs/schemas/agentic/four-verb/, and pins the L1↔L2↔L3 equivalence invariant.
depends_on:
  - vision/specs/02-tool-result-envelope.md
  - vision/specs/06-agentic-base.md
  - vision/specs/12-vocabulary.md
referenced_by:
  - vision/specs/09-crossover-matrix.md
  - vision/specs/10-harness-ladder.md
---

# 11-four-verb-canon

## §1 The four verbs

The cross-layer harness contract operates on exactly four verbs. They facilitate the entirety of tool discovery, execution, skill discovery, and skill dispatch.

| Verb | Request Schema | Response Schema | Purpose |
| ---- | -------------- | --------------- | ------- |
| `mcp__list_tools` | `list-tools-request.schema.json` | `list-tools-response.schema.json` | Discover available tools. |
| `mcp__call_tool` | `call-tool-request.schema.json` | `call-tool-response.schema.json` | Execute a specific tool. |
| `mcp__list_skills` | `list-skills-request.schema.json` | `list-skills-response.schema.json` | Discover available skills in a row. |
| `mcp__dispatch_skill` | `dispatch-skill-request.schema.json` | `dispatch-skill-response.schema.json` | Dispatch control to a specific skill. |

> **Note:** The schemas referenced are located at `vision/specs/schemas/agentic/four-verb/*.schema.json`. Two request schemas (`list-tools-request.schema.json` and `list-skills-request.schema.json`) are scheduled for Wave 1 creation.

## §2 The namespacing rule

Verb names ALWAYS carry the `mcp__` prefix. Bare `call_tool` or bare `dispatch_skill` is FORBIDDEN in `vision/` active prose.

This rule keeps schema citations unambiguous and fundamentally differentiates verb-on-MCP (a networked or inter-process semantic) from in-process function calls.

> **Audit Finding:** This rule specifically closes the finding at `vision/10-vision-audit-columns.md` §6 headline 5.

## §3 L1↔L2↔L3 equivalence invariant

The system enforces strict structural isomorphism across layers. This is proof obligation #1 from the alignment workflow.

**Invariant Formally Stated:**
For every layer L ∈ {L1, L2, L3}, every verb V in the canon, and every well-formed envelope E, the result tool_result T(V, E) is byte-equal (or semantically equal where stochastic elements like timestamps are involved) across L.

For context on L1, L2, and L3 layers, see `vision/specs/10-harness-ladder.md` §2 (the ladder north-star).

**Pinning Test:**
The invariant is anchored by the test at `tests/integration/test_devmode_server.py`.

## §4 No backdoors rule

The alignment workflow establishes proof obligation #4: No domain backdoors. Cross-column calls MUST route through the designated interface verbs.

Direct Python imports across column boundaries (e.g., `from agentic.<other_row>.handlers.<x> import handle`) are STRICTLY FORBIDDEN.

Cross-column calls MUST go through:
- `mcp__call_tool(name="mcp__<row>_<export>", ...)`
- `mcp__dispatch_skill(row, skill_slug, context_refs)`

> **Source Material:** See `vision/specs/09-crossover-matrix.md:151-156` for the §3.1 paragraph documenting this behavior.
> **Lint Enforcement:** This rule is mechanically verified by `tests/agentic/test_pretooluse_veto.py`.

## §5 Verb signatures

The canonical signatures below reflect exact wire representations per schemas:

- `mcp__list_tools()` → `{ok, data: {tools: [...]}, warnings, next_suggested_tools}`
- `mcp__call_tool(name, args)` → `{ok, data: {result}, warnings, next_suggested_tools}`
- `mcp__list_skills()` → `{ok, data: {skills: [...]}, warnings, next_suggested_tools}`
- `mcp__dispatch_skill(row, skill_slug, context_refs)` → `{ok, data: {result}, warnings, next_suggested_tools}`

> **Note:** `mcp__dispatch_skill` accepts exactly `(row, skill_slug, context_refs)` per `vision/specs/schemas/agentic/four-verb/dispatch-skill-request.schema.json`. Older docs depicting `mcp__dispatch_skill(name, args)` are STALE and slated for Wave 1/2 fixes.

## §6 The 4-key envelope

Every verb response MUST adhere exactly to the 4-key envelope shape defined in `vision/specs/02-tool-result-envelope.md`.

The core envelope shape is:
`{ok, data, warnings, next_suggested_tools}`

Extension slots in the `data` payload (e.g., `data.workflow_dispatch`, `data.artefact_ref`, `data.previous_continuation_id`) are introduced by spec 09 §3.2, and strictly do not break the 4-key shape at the root.

## §7 Done-When (Gherkin acceptance anchors)

```gherkin
Feature: Four-verb structural equivalence
  Scenario: four_verb.L1.list_tools
    Given an initialized L1 process
    When the mcp__list_tools verb is called
    Then the response shape exactly matches list-tools-response.schema.json
    And the envelope strictly adheres to the 4-key constraint

  Scenario: four_verb.L1.call_tool
    Given an initialized L1 process
    When the mcp__call_tool verb is called with a registered tool and valid arguments
    Then the response shape exactly matches call-tool-response.schema.json
    And the envelope strictly adheres to the 4-key constraint

  Scenario: four_verb.L3.list_tools
    Given an active L3 MCP daemon
    When the daemon receives an mcp__list_tools request via transport
    Then the daemon returns a response that matches list-tools-response.schema.json

  Scenario: four_verb.iso.L1_eq_L3
    Given an identical underlying state
    When mcp__call_tool is executed in L1
    And mcp__call_tool is executed over L3 with the identical payload
    Then the respective tool_result responses are byte-equal (excluding stochastic data)
```
