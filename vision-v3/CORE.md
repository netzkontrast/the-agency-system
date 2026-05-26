# agency — Core (v4, radically cut)

> Supersedes the v3 `VISION.md` / `DESIGN.md` drafts (kept alongside as the
> critiqued artifact). The adversarial panel (4/4) cut the 5W1H / six-domain
> model to its irreducible core. **5W1H is now a lens, not the architecture.**
> Names follow structure. The projection is an *observation*, not a mechanism.

## Four concepts + one substrate

**Substrate — the Engine.** One FastMCP server + one bi-temporal graph.
**Code-mode IS the contract** (lean — no four-verb surface): the public surface is
exactly `search` · `get_schema` · `execute`. The agent writes code in `execute`
that chains tools (`await call_tool(...)`); intermediate results stay in-sandbox,
only deltas cross into context. Tools are discovered via `search`. This one
contract is exposed **three isomorphic ways — MCP · Skills · a bash CLI** (the
harness-in-harness ladder) so a bash-only agent (Jules, no MCP/Skill) is a
first-class participant; proven in `seed/` (`AGENTS.md` + a bash↔MCP isomorphism
test). Cross-cutting guards (quality-score, loop-detection, compaction,
`Slot`/quota) are engine middleware, **not** concepts.

**1. Intent** *(human-owned).* A supersedable node carrying **purpose +
acceptance**, with the **deliverable as an attribute** (why/what merged).
`capture → confirm`, revised via `supersede`. **Everything edges back to it via
`SERVES`.**

**2. Capability** *(the craft — open set).* An invokable action. Verbs are
capability-defined and **role-tagged**: `act` (craft write) · `transform`
(stateless compute) · `effect` (external side-effect). Discover via
`<capability>.help` (progressive disclosure ↔ `SKILL.md`).

**3. Lifecycle** *(state + gates).* The task/agent state-machine. Verb frame:
**`open · move · close`** (write) + **`read · find · check · watch`** (observe).
States align with A2A tasks (`submitted · working · input-required · completed ·
failed · canceled`). **An agent (the old "who") is a Lifecycle parameterization**
— an agent-session is a lifecycle whose transitions/observers differ (a remote
async agent inserts `verify`; `COMPLETED ≠ done`). Gates = `input-required` →
Intent re-entry.

**4. Memory** *(the moat).* One bi-temporal, append-only graph holding **every**
node — Intent, Capability invocations, Lifecycle states, artefacts — and their
edges (`SERVES`, `PRODUCES`, `DISPATCHED_TO`, `PRECEDES`, `SUPERSEDES`). Verbs:
`record · link · supersede` + `recall · find · validate`. `project(query,
budget)` → ranked, token-budgeted, supersession-aware (`as_of`) deltas. **The one
thing the SDK-native rival cannot match:** cross-concern provenance is a *single
traversal* — "every action that `SERVES` intent Q1, the agent that ran it, the
gate it passed."

## Skills are atomic, gated, progressively-disclosed step-graphs

A "skill" is **not** a monolithic `SKILL.md` loaded wholesale. In v4 a skill is a
**Lifecycle template: a graph of atomic Capability steps + Gates**, walked
step-by-step via code-mode. Each step discloses only the *next* instruction
(`search → get_schema → execute`), so tokens are paid per atomic step, not for
the whole skill. The chain *is* an executable dataflow graph, and because every
`call_tool` records an Invocation, it mirrors itself into the provenance graph.

**Gates / intent-verification / human-in-the-loop are `elicit` steps.** A step
can `ctx.elicit(prompt)` (ask the agent or human a one-line question and get a
typed answer), `ctx.sample(...)` (ask the caller's LLM), or `ctx.report_progress`
(stream). A gate that needs a human is just an `elicit` → the Lifecycle pauses at
`input-required`, the answer resumes it, the outcome is recorded as a `Gate`.
"askuser" is therefore not a special case — it is one node in the chain. All of
this is proven runnable in `../agency-seed/` (real `ctx.elicit` round-trip).

## Schemas & templates (the typed/generative layer)

Both are ordinary nodes in **Memory**, forming a generate/validate pair:
- A **Schema** is the typed contract for a node / artefact / verb-params. It powers
  `validate` / `check` — and it is the **isomorphism glue**: one schema per verb
  renders three ways (MCP `inputSchema`, the Skill's frontmatter, the bash CLI's
  arg parser), which is *why* MCP / Skill / bash stay in lockstep.
- A **Template** is a parameterized generator. It powers `act`: a Capability
  produces an Artefact `DERIVED_FROM` the Template, which `VALIDATES_AGAINST` its
  Schema.

Proven runnable in `seed/` (a Template renders an Artefact that a Schema
validates; a missing field fails). This is how a real capability ports: its verbs
(Capability) + its schemas/templates (Memory) + its pipeline (Lifecycle).

## Dropped (and why)

- **Six-domain 5W1H** → a lens, not structure (journalistic checklist, not an
  execution theorem).
- **why/what as two domains** → merged into Intent (no workflow needs them split).
- **`(home,target)` projection as a total function** → demoted to an optional
  observation (Cyc/RDF/Ranganathan: total decomposition always leaks). No
  generating function; the AOP escape hatch is therefore unnecessary.
- **Three name renderers** → a serializer detail, not a top-level concern.

## Kept (panel-endorsed)

The **isomorphic verb frame**; the **one bi-temporal provenance graph +
`SERVES`**; **code-mode as the one lean contract** (exposed isomorphically over
MCP / Skills / bash); the **`COMPLETED ≠ done`** lesson.

## Naming

Structure-first. Concepts: `intent`, `capability`, `lifecycle`, `memory`. Tool
names `<concept>_<capability>_<verb>` (underscores, ≤64, no dots; the client
injects `mcp__`).

## Status: the seed proves it (10/10 green, `seed/`)

Built on the real substrate (graphqlite + fastmcp + Monty). Proven runnable:

- the **provenance moat** (one traversal);
- **two genuinely different capabilities** — a stateless `transform` and the
  **REAL Jules agent** wired to the actual orchestrator (`jules_create`/`get`);
- **bi-temporal memory** (`as_of`); **`COMPLETED != done`** (real Jules `verify`:
  state completed AND a branch on origin);
- **code-mode is the contract** (`search`/`get_schema`/`execute`) — exposed
  isomorphically over MCP and a **bash CLI** (Jules-dogfooded, PR #175);
- **code-mode tool-chaining**; **gates via `elicit`**;
- **schemas & templates** (typed/generative layer);
- a **strictly enforced ontology** (`ontology.py`: per-node required-field schemas
  + an enumerated edge set + closed enums; `record`/`link` reject drift);
- a **micro-step skill walker** (`skill.py`): walks `ALBUM_CONCEPT_SKILL` — the
  real bitwize conceptualizer schematized — one phase at a time (progressive
  disclosure, token-efficient) through its Phase-7 **hard gate**, recording each
  phase as provenance.

Next: grow the capability set (port more bitwize crafts as strict schemas) and
graduate the seed into the shipped engine.
