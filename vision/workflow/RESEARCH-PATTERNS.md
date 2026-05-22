# Workflow Patterns Research

## 1. Inventory

### Repo: `netzkontrast/the-agency-system` (this repo)
- `Plan/phase-8-operational-hardening`: Mentions workflow learnings and CI workflow.
- `servers/agency-mcp/src/agency_mcp/handlers/music/gates.py`: Implements hard-blocking checks between music phases.
- `servers/agency-mcp/src/agency_mcp/handlers/novel/gates.py`: Implements hard-blocking checks for novel phases.
- `skills/music/sheet-music-publisher/workflow-detail.md`: Deep dive into a specific domain workflow.
- `.claude/journal/dispatch/dispatch_workflow_learnings.py`: Tool/Script tracking workflow learning artifacts.
- `.claude/journal/jules-wave3-workflow-learnings.jsonl`: Logs of workflow learnings.

### Repo: `netzkontrast/agency` (legacy MVP)
- `TASK.md:215-256`: Defines the `/sc:analyze → /sc:brainstorm → /sc:design → /sc:workflow` ladder for decomposition.
- `skills/sc-workflow/SKILL.md`: Defines the workflow-generator skill. Extracts tasks into `tasks/<NNN>-<slug>/workflow.md`.
- `skills/novel-architect/phases/phase0-bootstrap.md` - `phase7-iteration.md`: Progressive disclosure markdown files for Roman development phases.
- `skills/novel-architect/phases/phase5-scene-matrix.md`: Shows a 3-gate approval system within a single phase.
- `skills/research-prompt-optimizer/phases/`: Defines a 5-phase pipeline for prompt research.

## 2. Vital Patterns
1. **The Phase Ladder (from `TASK.md:215`)**: A strict progression `analyze → brainstorm → design → workflow`. Preserving this enforces logical decomposition before execution.
2. **Progressive Disclosure (from `skills/novel-architect/phases/readme.md:2`)**: Loading phase-specific markdown files (`phaseN-*.md`) only when needed. Prevents context bloating.
3. **Multi-Gate Phases (from `skills/novel-architect/phases/phase5-scene-matrix.md:20`)**: A single phase having internal sub-phases and distinct `GATE N` checkpoints (e.g., auto + askuser).
4. **Separation of Planning and Execution (from `skills/sc-workflow/SKILL.md:22`)**: `sc-workflow` ONLY plans. Execution is deferred to another agent/skill.
5. **Executable Workflow Contracts (from `TASK.md:229`)**: The workflow document is the executable contract, discoverable from the Task folder, allowing future agents to reconstruct provenance.

## 3. Anti-patterns
1. **Scattered Workflow Definitions**: In the legacy repo, workflow files are found under `tasks/`, `skills/`, `prompts/`, and `research/`. This violates the `workflow/` column invariant.
2. **Hidden Execution in Planners**: Planners attempting to write code or run builds directly (specifically called out to avoid in `skills/sc-workflow/SKILL.md:30`).
3. **Informal Gate Checking**: Relying on the agent to "just remember" to check things, rather than using mechanical constraints (addressed by `tools/check-governance.sh` in the new repo).

## 4. Constraints from other columns
- **Agentic Constraint**: Handlers are strictly stateless (`vision/agentic/COLUMN.md:46`). Workflow must pass all necessary state context through the invocation envelope (`execute_pipeline`).
- **Context Constraint**: Artefacts must reside in standard storage vaults (`vision/context/INTERFACE-TO-WORKFLOW.md:14`) and schema validation must be handled by context. Workflow should only emit the path/schema identifier.

## 5. Recommendations for `COLUMN.md`
1. Enforce Progressive Disclosure: Mandate that `phases/*.md` files are loaded lazily, not concatenated at pipeline start.
2. Formalize Sub-gates: Update the `manifest.toml` schema to allow multiple gates *within* a phase, not just between phases.
3. Explicit State Handoff: The Handoff Envelope must include an opaque `state_token` or `context_refs` array to bridge the stateless Agentic handlers.
4. Extract Planning from Execution: Explicitly forbid `workflow` pipeline definitions from performing code modifications directly; they must only compose `agentic` skill dispatches.
