## Summary
The highest-leverage spec-driven-development gap for the Jules plugin is the lack of a structured, multi-phase planning ladder that precedes code execution, and an explicit mechanism to update tasks as code naturally drifts. While `JULES_PROTOCOL.md` and Spec 099 enforce pre-commit checks and token discipline, they omit the rigorous pre-code "Design & Workflow" decomposition and the "PM-Mode Initialisation" validation layer present in `SuperClaude_Framework` and `superpowers`. Adopting a formal planning ladder (like `/sc:analyze -> brainstorm -> design -> workflow`) and a reflexive memory/context contract will prevent Jules sessions from heading in the wrong direction before any code is written, producing massive token savings and lower failure rates.

## Source repos surveyed
| repo | commit SHA | key files cited |
|---|---|---|
| netzkontrast/agency | (HEAD) | `TASK.md`, `decisions/0001-mandatory-session-bootstrap.md`, `templates/task.md` |
| netzkontrast/SuperClaude_Framework | (HEAD) | `PLANNING.md`, `PR_DOCUMENTATION.md`, `KNOWLEDGE.md` |
| netzkontrast/superpowers | (HEAD) | `README.md`, `skills/writing-plans/SKILL.md`, `skills/executing-plans/SKILL.md` |

## Patterns found
1. **Four-Stage Planning Ladder (/sc:analyze -> brainstorm -> design -> workflow)**
   - *Source:* `agency/TASK.md` (§4.9) and `SuperClaude_Framework/PLANNING.md`
   - *Description:* Enforces a strict, step-by-step socratic discovery and architectural design phase prior to any implementation, resulting in a locked `workflow.md`.
   - *Delta:* `JULES_PROTOCOL.md` expects a solid plan but doesn't mandate a formal, multi-stage decomposition artifact before Gate 1 (Confidence).
   - *Leverage:* High. Prevents the agent from executing code based on shallow plans or unverified assumptions, dramatically reducing wrong-direction work.

2. **PM Mode Context Contracts & Reflexion Memory**
   - *Source:* `SuperClaude_Framework/PR_DOCUMENTATION.md`
   - *Description:* Automatically initializes a project-specific "Context Contract" and a "Reflexion Memory" at the start of a session to strictly enforce project rules and prevent repeating past mistakes.
   - *Delta:* Spec 099 has a static `check_affects.py` and `JULES_PROTOCOL.md` has an anti-pattern list, but no dynamic "reflexion memory" or project-rule contract that validates intent *before* execution.
   - *Leverage:* Very High. Pre-execution validation catches structural errors and rules violations before any tokens are spent on coding.

3. **Subagent-Driven Development Checkpoints**
   - *Source:* `superpowers/skills/executing-plans/SKILL.md`
   - *Description:* Implementation plans are executed in small batches (e.g., 3 bite-sized steps) with mandatory pauses for "architect review" between batches.
   - *Delta:* `JULES_PROTOCOL.md` requires Gate 4 self-review post-implementation, but does not dictate batch execution with intermediate architectural checkpoints during the Do phase.
   - *Leverage:* Medium. Helps catch compounding drift early in long sessions.

4. **Task Lifecycle Management (Status: Updated/Abandoned)**
   - *Source:* `agency/TASK.md` (§4.7)
   - *Description:* Formalises when a plan is obsolete due to codebase drift, requiring a `task_supersedes` linkage and a friction log rather than just silently dropping work or forcing completion.
   - *Delta:* Not covered by Spec 134/135 or 099; current `JULES_PROTOCOL.md` handles failed sessions via API extraction but lacks a semantic state for "Spec Drift / Obsolete".
   - *Leverage:* Medium. Cleanly handles specs that become inaccurate due to concurrent merged PRs.

5. **Pre-Execution Validation Infrastructure (5 Core Validators)**
   - *Source:* `SuperClaude_Framework/PR_DOCUMENTATION.md`
   - *Description:* 5 validators (security, dependencies, runtime, tests, contracts) run automatically to block problematic code paths before execution begins.
   - *Delta:* Spec 099 adds `check_affects.py` and install consistency checks, but lacks comprehensive runtime/dependency pre-validators.
   - *Leverage:* High. Shifts failure discovery left, guaranteeing dependencies/contracts are sound before drafting files.

## What the existing Plan/ cluster already absorbs
- **Mandatory Clean Install & Pre-Commit Testing**: `JULES_PROTOCOL.md` Gate 3 and Spec 099 (Lines 19-20) already require `pip install -e . && cd /tmp` and capturing clean test output.
- **Review Subagent Dispatch**: Spec 099 (Line 21) introduces a dispatch independent review subagent (Gate 4), absorbing post-implementation validation.
- **Strict Scope Boundaries (`affects:`)**: Spec 099 (Lines 26, 29) creates `check_affects.py` to enforce that only permitted files are touched, absorbing basic scope limitation.
- **Automated Governance Checking**: Spec 099 introduces `check_install_consistency.py` (Line 27) and Spec 134/135 handle ADR substrate and trace linkages, absorbing architectural tracking.

## Proposed follow-up spec slots
- `jules-planning-ladder`: Implement the 4-stage `/sc` pipeline (`analyze -> brainstorm -> design -> workflow`) as a mandatory pre-requisite for complex Structural (T3) specs.
- `jules-reflexion-memory`: Introduce a dynamic Context Contract and Reflexion Memory loaded at session start to enforce project-specific rules (like Kong/Infisical rules) and avoid repeat failures.
- `jules-task-lifecycle-drift`: Add explicit `superseded_by` and `abandoned` states to the spec execution lifecycle to gracefully handle spec-code drift without forcing a `FAILED` session.

## Out of scope / questions for the orchestrator
- **Out of Scope:** Actually authoring the `.md` templates for the `/sc` ladder or modifying the runtime MCP fast server to intercept state. We only identified the structural gap.
- **Out of Scope:** Resolving exactly how a "Reflexion Memory" persists across parallel sessions (e.g. SQLite vs. JSON vs. `agency_mcp.state.cache.StateCache`).
- **Question for Orchestrator:** Do we want to strictly adopt the `SuperClaude_Framework` `/sc:*` skill names, or adapt them to match the `jules-planning-*` nomenclature natively in the plugin?
- **Question for Orchestrator:** Should the `superseded_by` / `abandoned` states be exposed as status enums via MCP to the host IDE/Claude, or kept strictly as markdown frontmatter attributes?
