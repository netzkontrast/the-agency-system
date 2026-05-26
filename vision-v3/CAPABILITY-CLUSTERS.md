# Capability clusters — surveyed, clustered, spec-paneled

> How this was produced (the loop): three agents surveyed **every installed
> plugin** — superpowers (14 skills) + private-journal, bitwize-music (~54 skills,
> ~72 MCP tools), and the agency-marketplace (~58 skills + a workflow/context/jules
> runtime). A clustering agent grouped the findings into candidate capabilities. An
> adversarial spec panel then **integrated them as concepts** against the v4 core.
>
> **Disposition rule (per directive):** only **skill-creation** and
> **plugin-development** are *full ports* (built — see `../agency/`). Everything
> else is integrated **as a concept/spec**, not code.

## The 12 candidate clusters

| Cluster | Role(s) | Absorbs (sources) | Concept | Disposition |
|---|---|---|---|---|
| `author-skill` / `plugin-dev` | act, process | writing-skills (sp); plugin/marketplace authoring; setup/health (bitwize) | Capability + Lifecycle + Engine | **full-port (built)** |
| `delegate` | agent, effect | dispatching-parallel-agents, requesting/subagent-driven review (sp); jules-orchestrator + fan-out/bulk + discipline (agency-mp); release-director, researcher-lead (bitwize) | Capability + Lifecycle + Memory | concept-spec |
| `gate` | transform, process | Gate Evaluator + phase-gate-envelope (agency-mp); verification-before-completion, receiving-code-review (sp); lyric/explicit/plagiarism/voice/pronunciation reviewers, validate-album, qc_audio, verifier, pre-generation-check (bitwize) | Lifecycle + Memory | concept-spec |
| `walk-phases` | process, Engine | Pipeline Runner + Envelope state + Manifest Reader (agency-mp); executing-plans (sp); album-conceptualizer 7-phase (bitwize) | Lifecycle + Engine | concept-spec |
| `craft` | act | lyric-writer, suno-engineer, art-director, promo, sheet-music, mix/mastering, genre, new-album (bitwize); writing-plans, brainstorming (sp) | Capability + Intent + Memory | concept-spec |
| `transmute` | transform | CodeMode tool-list shaping, anchor tools, patch-summary (agency-mp); state indexer/parsers, help/about (bitwize) | Engine + Capability | concept-spec |
| `commit-effect` | effect | finishing-a-branch, git-worktrees (sp); silent-fail-recovery (agency-mp); import/rename/promote/clipboard/cloud, document-hunter (bitwize) | Lifecycle + Memory + Engine | concept-spec |
| `research` | agent, transform | researcher + 9 domain specialists + verifier, document-hunter (bitwize); research+verification chains (agency-mp) | Capability + Memory + Lifecycle | concept-spec |
| `reflect` | act, transform | journal entries by scope + semantic-search + retrieval (private-journal) | Memory + Intent | concept-spec |
| `navigate` | transform | resume, dashboard, next-step, state-nav (bitwize); envelope read-views (agency-mp) | Lifecycle + Memory + Intent | concept-spec |
| `discipline` | process | TDD, systematic-debugging, subagent-driven-development (sp); context-safe-patch, jules-orchestrator-discipline (agency-mp) | Lifecycle | concept-spec |
| `wire-handlers` | Engine, effect | Cell Loader + CodeMode integration + Store protocol + hooks (agency-mp); ~72 MCP tools + PostToolUse hooks (bitwize) | Engine + Memory | concept-spec |

## Panel verdict — collapse onto the four concepts

The v4 panel's discipline ("5W1H is a lens, not the architecture") applies again:
**most clusters are facets of the existing four concepts, not new primitives.**
Multiplying top-level concepts would re-introduce the six-domain bloat v4 cut.

- **`gate` · `discipline` · `walk-phases` are three faces of Lifecycle.** A gate is
  a *predicate* (a transition precondition), a discipline is a *policy* (an ordering
  constraint), walk-phases is the *executor* (the skill walker). Keep
  predicate/policy/executor distinct but all **inside Lifecycle** — they are not new
  concepts. *Already realized:* `skill.py` is the executor; the hard gate + the
  `lint_skill`-as-compute is a gate; the `SKILL_CREATION_SKILL` Iron Law (GREEN
  unreachable until RED produced its baseline) is a discipline **enforced by
  ordering**.
- **`craft` · `transmute` · `commit-effect` are just the role-tags `act` /
  `transform` / `effect`.** They are not concepts; they are the open Capability set.
  The `plugin` capability already instances `act` + `transform`; `jules` instances
  `effect`.
- **`reflect` is Memory-scoped `craft` + a `recall`/`search` transform.** Since
  Memory is one graph, journaling is a capability that writes scope-tagged nodes and
  a transform that retrieves them — not a separate store.
- **`navigate` is a read-projection over Lifecycle+Memory** — i.e. `Memory.project`
  / `provenance` with an "unsatisfied-gates vs acceptance" view. Already the moat.
- **`wire-handlers` is the Engine substrate** — and the agency engine now does the
  reusable half of it: **reflection-based discovery + auto-wiring** (`discover()` +
  `inspect.signature`), the agency analog of the marketplace's Cell Loader.
- **`research` is a *composition*, not a primitive** — `delegate` (fan-out to
  specialists) → `craft` (source nodes) → `gate` (the verifier). Ship it as a **skill
  template**, not a capability.

## What is genuinely net-new (the next specs)

After the collapse, exactly **one** primitive is missing from the engine, and one
capability is high-value enough to spec explicitly:

1. **`delegate` (agent role) — the spec worth building next.** An agent IS a
   Lifecycle parameterization; `delegate` spawns a *child* Lifecycle with a scoped
   Intent, a context budget, and an acceptance contract, then **fans out** N siblings
   under a quota ceiling and **joins** on their terminal states. New edges:
   `DELEGATES_TO`, `REDUCES_INTO`. `jules` is the single-child reference
   implementation; the fan-out/quota/join is the generalization. This is what lets
   the engine scale past one context.
2. **`reflect` (Memory capability).** Scope-tagged insight nodes
   (`OBSERVED_DURING`, `INFORMS`) + recency/semantic retrieval — the durable
   cross-session memory the private-journal proves is valuable, expressed as one
   capability over the one graph.

Everything else in the survey is **already expressible today** as capabilities
(`act`/`transform`/`effect` verbs), skills (Lifecycle templates of phases + gates),
or engine substrate — no new architecture required.

## Confidence

~0.9 that the four concepts + the engine absorb the entire surveyed surface, and
that `delegate` + `reflect` are the only net-new specs worth carrying forward. The
residual 0.1: `delegate`'s join/quota semantics and `reflect`'s retrieval ranking
are unproven until built (the same falsification bar the rest of the seed met).
