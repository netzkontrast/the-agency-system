# agency — Design Specs (v3 draft, for adversarial review)

> Status: DRAFT under a ≥0.95 confidence gate. Each section is an initial spec
> of one system part + how it interacts with the others. "specced — not built."

## 0. Topology

ONE FastMCP engine + ONE GraphQLite graph (bi-temporal, append-only). Six
domains: two human (why, what) + four execution (who, how, when, where).
Capabilities are authored into domains; the engine + graph are the substrate.

## 1. The engine (NOT a domain)

- **Four-verb meta-contract:** `list_tools`, `call_tool`, `list_skills`,
  `dispatch_skill` — the only cross-surface. MCP has no skill RPC, so
  `list_skills`/`dispatch_skill` are themselves surfaced as MCP tools.
- **Code-mode call surface:** the domains are rendered as a typed code API; the
  agent writes code through one `execute(code)` tool; intermediate results stay
  in-sandbox; large payloads return as `elided_ref` handles; only filtered
  deltas reach context (Anthropic "Code execution with MCP", 2025-11-04 — up to
  −98% tokens). Every code-callable function is ALSO a registered MCP tool, or
  it is invisible to MCP clients.
- **Engine guards (cross-cutting, not domains):** quality-score, loop-detection,
  compaction checkpoints, `Slot`/quota accounting.

## 2. The six domains

- **why** (human) — purpose + success criteria. Owns acceptance.
- **what** (human) — the object/deliverable. Owns subject identity.
- **who** — the agent/role that performs; agent-session lifecycle; dispatch,
  handoff, supervision; harness-in-harness.
- **how** — the craft: skills, tools, actions. The *open* domain.
- **when** — the task/process lifecycle: order, gates, scheduling, triggers.
  Owns the interaction state-machine (§5).
- **where** — memory: the bi-temporal append-only graph + artefacts.

## 3. Capabilities, home, and projections (multi-domain model)

A **capability** (jules, music, novel) declares ONE **home domain** = its
TYPE/essence (faceted classification; Ranganathan's primary facet). Its
cross-sections in the other domains are **projections**, derived by a **total,
deterministic `(home, target)` function** — store one home label, *generate*
the three other aspects. Projection table:

| home ↓ | → who | → how | → when | → where |
|---|---|---|---|---|
| **who** (jules) | — | skills it wields | its session/turn lifecycle | its memory scope / working set |
| **how** (a skill) | who is licensed to perform it | — | the step where it applies | artefacts it reads/writes |
| **when** (music pipeline) | pipeline roles-as-actors | technique invoked per stage | — | state transitions / checkpoints |
| **where** (a schema) | owner/scope of the node | retrieval/write op | retention/expiry lifecycle | — |

The shape is the *pair* `(home, target)`: the same target (`when`) yields a
**session** for a who-home but a **step** for a how-home. That is the
isomorphism the home buys.

**AOP escape hatch:** genuinely cross-cutting capabilities with no natural home
(`verify`/QC, observability, memory-as-concern) are modeled as **aspects woven
across all four domains**, not forced into a home.

Aspects materialize **lazily** (lazy-domaining): an aspect exists only when
needed; the holding domain owns it. No eager 4× triplication.

## 4. The verb model

**Closed domains (who/when/where)** share a two-axis frame:
- **Lifecycle (write):** `open · move · close`
- **Observe (read):** `read · find · check · watch` (`check` = validate against
  rules; `watch` = continuous monitor — they are different operations)

Canonical verbs:

| domain | open | move | close | read | find | check | watch |
|---|---|---|---|---|---|---|---|
| **who** | dispatch | handoff | release | poll | roster | verify | watch |
| **when** | start | advance | complete | status | list | check-gate | watch |
| **where** | record | link | supersede | recall | find | validate | — |

**how (open):** capability craft-verbs (`master`, `patch`, `lyric`), each
**tagging a role**: `act` (craft write) · `transform` (stateless compute, e.g.
`count_syllables`) · `effect` (external side-effect, e.g. clipboard). Discovery
via mandatory `how.<capability>.help`.

A specialist verb is allowed in any closed domain but **must declare its frame
role**; the canonical role surfaces as a call-site **alias**
(`where.music.supersede` ≡ `where.music.close`).

Extra `who` orchestration verbs beyond the frame: `retry`/`respawn` (with the
canon guard: never respawn jules if a patch already exists; do if empty),
`escalate`, `fan_out`, `reclaim_slot`.

## 5. The interaction state-machine (owned by `when`)

`when` owns the lifecycle. Its **states** align with A2A task states:
`submitted · working · input-required · auth-required · completed · failed ·
canceled · rejected`. Verbs **drive** transitions (start/advance/complete);
`status`/`watch` **observe**. **Gates = `input-required`** → the human (why/
what) re-enters to clarify/approve/redirect (and may amend intent → supersede
the intent node). `who` **parameterizes** the machine: a remote async agent
inserts `poll`/`verify` states (COMPLETED ≠ done) a local subagent skips. The
`who`↔`when` join is a `DRIVES` edge (a who-session DRIVES a when-task),
written by `when` (it owns the lifecycle); state is never duplicated.

## 6. Naming — three renderers from one logical name

- **Logical / code-mode / human:** `domain.capability.verb` (dotted — human
  notation only).
- **MCP tool:** `domain_capability_verb` — underscores, ≤64 chars, no dots,
  avoid hyphens (Claude frontend `^[A-Za-z0-9_]{1,64}$`); never bake in `mcp__`
  (the client injects it).
- **Skill (`SKILL.md`):** `domain-capability-verb` — hyphens, lowercase, equals
  the folder name; `skill_kind` rides in `metadata:`.
- **A2A `AgentSkill` id:** free-form.

A name-mapping table keeps one logical verb resolvable across all three.

## 7. `where` — memory

Bi-temporal, append-only GraphQLite graph; `supersede` never overwrites;
supersede semantics encoded in resource URIs / metadata.
`where.project(query, budget) -> ranked deltas`: `as_of` filter (only
valid-as-of) → hybrid retrieve (BM25 + semantic + graph BFS) →
RRF / MMR / node-distance + recency blend → **token-greedy cut** (not fixed
top-k) → community-summary fallback → return deltas with provenance
(`valid_at`, `invalid_at`, score). Artefact drivers (fs/repo/s3/http/drive):
bytes live in user storage, the graph holds metadata only.

## 8. `who` — agents & harness-in-harness

Agents/roles (jules, codex, local-subagent, orchestrator) declared in an
`agents.yaml`-style manifest. Nodes: `Agent`, `Role`, `Dispatch` (per-hop
correlation id), `SharedContext` (handoffs pass context, not just a baton),
`Slot`. **A2A boundary adapter:** external agents are exposed as Agent Cards and
driven as A2A **Tasks**; the Task-ID is the cross-harness correlation key. The
four-verb contract is the internal MCP/tool plane; `who.dispatch/handoff` is
agency's internal handoff primitive (like Claude-SDK subagent-spawn). Note:
Claude subagents cannot self-nest — correlation must be explicit.

## 9. `how` — craft

The open domain. Capability-specific verbs, each role-tagged (act/transform/
effect). Maps to the Agent Skills spec (a capability ↔ a `SKILL.md` folder);
`how.<cap>.help` ↔ progressive disclosure (metadata → body → references).

## 10. `why` / `what` — the human domains

Two distinct human domains with **independent-but-linked lifecycles**: the
`what` can change while the `why` holds, and vice-versa. `why.capture`/
`why.confirm` and `what.capture`/`what.confirm` (interview + critical-thinking).
Persisted as Intent nodes, pinned once + referenced by id (cache-safe). Every
action edges back via `SERVES_WHY` / `SERVES_WHAT`. Surface-maps to MCP prompts
(templates); persistence stays internal.

## 11. Context-engineering commitments

Progressive disclosure (cold-boot exposes only the four meta-verbs; domain
verbs load on demand); code-mode deltas; append-only bi-temporal graph +
`where.project`; compaction (`compact-2026-01-12`) + memory tool; ephemeral
subagent isolation (return 1–2k-token summaries); append-only stable KV-cache
prefixes; tool-masking not tool-removal; TOON for graph projections when
tabular-eligibility > 0.8, else JSON.

## 12. Worked example — "fix the failing auth test, via jules"

1. `why.capture`/`what.capture` → `confirm` → Intent nodes (`why:Q1`,
   `what:auth-test`).
2. `who.dispatch(role=jules)` (chosen from `what`) → `Dispatch` node, `DRIVES`
   edge to a new `when` task.
3. `when.start` → states `submitted→working`; phases investigate→patch→verify→
   PR; gate `tests-green`.
4. `how.jules.patch` (role=act) applies the fix.
5. `where.record` + `where.link` the patch + results, `SERVES_WHAT`/`SERVES_WHY`.
6. `who.poll` / `who.verify` — COMPLETED ≠ done; verify branch on remote.
7. gate fails for human input → state `input-required` → human confirms via
   `why`/`what`.
8. `when.advance` (gate green) → `who.handoff(role=codex)` (jules→codex→human).
9. `when.complete` (state `completed`) · `who.release`.

## 13. Scope — full concept, minimal proof

Document the full model; **build** only jules (home = who) + lazy aspects + the
worked example. Everything else is **specced — not built**.

## 14. Known open seams (seed for adversarial review)

- Does the `(home, target)` projection stay **total & deterministic** across
  real capabilities, or does it leak into hand-authoring?
- Is the AOP escape hatch a clean boundary, or a slope where everything claims
  "cross-cutting"?
- Is **six domains** right, or over-decomposition? Could 3–4 suffice?
- Two human domains (why/what) as first-class — earns its complexity, or
  ceremony?
- `when` owning the state-machine vs an engine orchestration layer — coupling risk.
- Three name renderers — a maintenance burden / drift source?
- Does any of this beat "just use the Agent SDK + a flat tool list + a memory
  tool"?
