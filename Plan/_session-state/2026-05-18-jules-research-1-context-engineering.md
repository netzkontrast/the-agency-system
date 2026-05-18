## Summary
The highest-leverage pattern discovered is the **PM Agent Confidence Check** from the SuperClaude Framework, which yields a 25-250x token ROI by enforcing a pre-execution requirement check. While hybrid search and subagent workflows offer value, shifting confidence validation to the start of the orchestration pipeline prevents compounding errors. The `the-agency-system` should adopt PM Agent style confidence checks before launching implementation tasks.

## Source repos surveyed
| Repository | Commit SHA | Key Files Cited |
|---|---|---|
| `claude-context` | f794b8cae6b1e2f03fc105547f2785a7c9f6dc06 | `packages/core/src/sync/merkle.ts`, `README.md` |
| `SuperClaude_Framework` | 22ad3f483a6fe6c626834e1c9a3573126644a058 | `KNOWLEDGE.md`, `PROJECT_INDEX.json` |
| `superpowers` | b9e16498b9b6b06defa34cf0d6d345cd2c13ad31 | `skills/brainstorming/SKILL.md`, `skills/subagent-driven-development/SKILL.md` |

## Patterns found

1. **PM Agent Confidence Checking** (`SuperClaude_Framework`, `KNOWLEDGE.md`, Lines 10-25)
   - **Description**: An explicit pre-execution assessment that gates implementation tasks. If the confidence score (based on task clarity, constraints, and constraints) falls below 0.70, execution halts and human clarification is requested.
   - **Differs from 108/111-113**: Not present. The 111-chain focuses on context ingestion and cache efficiency, while this is a behavioral orchestration guardrail.
   - **Leverage**: High. It drastically reduces wasted tokens on wrong-direction work.

2. **Subagent-Driven Development** (`superpowers`, `skills/subagent-driven-development/SKILL.md`, Lines 1-20)
   - **Description**: A two-stage implementation loop per task: execution is handled by a fresh subagent, followed by a strict compliance check, then a code quality check.
   - **Differs from 108/111-113**: 108 provides hook integrations but lacks this strict intra-session recursive loop for independent plan execution.
   - **Leverage**: High. Isolates context bloat by relying on localized context for individual tasks.

3. **Merkle-DAG Incremental Synchronization** (`claude-context`, `packages/core/src/sync/merkle.ts`, Lines 1-30)
   - **Description**: Uses a Merkle Tree architecture to selectively index only files that have been modified (by computing and comparing SHA-256 hashes), persisting state to speed up synchronization.
   - **Differs from 108/111-113**: Spec 113 (`context-cache-and-subscriptions`) polls `os.stat` with fallback hashing over a linear manifest. A Merkle-DAG approach is more structurally robust for deeply nested directories but more complex.
   - **Leverage**: Medium. File system polling in 113 is likely sufficient for Wave B scale, making the Merkle approach over-engineered right now.

4. **Socratic Brainstorming Mode** (`superpowers`, `skills/brainstorming/SKILL.md`, Lines 5-25)
   - **Description**: An explicit skill invoked prior to design/implementation that enforces a one-question-at-a-time paradigm to tease out edge cases and user constraints.
   - **Differs from 108/111-113**: Completely orthagonal to document ingestion. It is a user-facing dialogue interaction pattern.
   - **Leverage**: High. Resolves ambiguity upstream before the orchestration DAG is instantiated.

5. **Pre-computed Project Index** (`SuperClaude_Framework`, `PROJECT_INDEX.json`, Lines 1-50)
   - **Description**: A static JSON manifest tracking core modules, execution flows, tests, and token efficiency metrics, shrinking context ingestion from 58,000 to 3,000 tokens.
   - **Differs from 108/111-113**: Spec 111 (`context-manifest`) is similar, but the SuperClaude approach embeds explicit project principles, dependency metrics, and git-workflow instructions natively into the structural JSON index.
   - **Leverage**: Medium. Validates the 111-chain approach but suggests enriching `context_manifest.json` with metadata.

## Recommendation: 108 vs 111-chain
The project should adopt the **111-chain (Build from Scratch)** path instead of Spec 108 (Context-Mode Integration).
**Evidence**: The survey demonstrates that custom architectures like SuperClaude's Project Index and powers' skills (Brainstorming, PM checks) tightly couple data extraction with orchestration workflows (e.g., confidence gating). Building the context tools from scratch (Specs 111-113) provides exact control over token chunking, prompt-cache breakpoints, and custom FastMCP lifecycle hooks, avoiding the dependency risk of relying on a third-party, TypeScript-based local HTTP `/ctx-insight` service (mksglu/context-mode) which might misalign with `the-agency-system`'s specific Python DAG.
**Abandonment Cost**: Discarding Spec 108 means giving up instant, drop-in integration with the 26 canonical context-mode hooks and pre-built Think-in-Code prompts.

## Proposed follow-up spec slots
- `114-pm-agent-confidence-check`: Implement pre-execution token-saving confidence gates (SuperClaude pattern).
- `115-socratic-brainstorming-skill`: Build the `superpowers:brainstorming` collaborative design skill.
- `116-subagent-driven-development`: Formalize the two-stage (compliance then quality) independent subagent execution loop.

## Out of scope / questions for the orchestrator
- `claude-context` is built on TypeScript/Node (`packages/core`); do we need to port its AST-based chunking logic to Python, or rely purely on markdown boundaries?
- Is the Merkle-DAG complexity necessary over Spec 113's linear `os.stat` polling? (Current assessment says no).
- For `114-pm-agent-confidence-check`, should confidence scores be mathematically derived (formulaic) or LLM-intuited during evaluation?
