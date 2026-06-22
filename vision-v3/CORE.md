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
first-class participant; proven in `../agency/` (`AGENTS.md` + a bash↔MCP isomorphism
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
this is proven runnable in `../agency/` (real `ctx.elicit` round-trip).

## Schemas & templates (the typed/generative layer)

Both are ordinary nodes in **Memory**, forming a generate/validate pair:
- A **Schema** is the typed contract for a node / artefact / verb-params. It powers
  `validate` / `check`. **Design intent:** one schema per verb renders three ways
  (MCP `inputSchema`, the Skill's frontmatter, the bash CLI's arg parser) — the
  *isomorphism glue*. *(Not yet wired: in the seed the MCP `inputSchema` is derived
  by FastMCP from the verb signature; making the ontology schema the single source
  is the next step.)* In the seed today the ontology IS enforced on the graph
  (`record`/`link` reject missing fields, broken enums, and unknown edges).
- A **Template** is a parameterized generator. It powers `act`: a Capability
  produces an Artefact `DERIVED_FROM` the Template, which `VALIDATES_AGAINST` its
  Schema.

Proven runnable in `../agency/` (a Template renders an Artefact that a Schema
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

## Status: the installable `agency` plugin proves it (19/19 green, `../agency/`)

The seed has **graduated into an installable Claude Code plugin** (`../agency/`).
Built on the real substrate (graphqlite + fastmcp + Monty). Proven runnable:

- the **provenance moat** (one traversal);
- **two genuinely different capabilities** — a synchronous craft/compute
  (`plugin`) and the **REAL Jules agent** wired to the actual orchestrator
  (`jules_create`/`get`);
- **bi-temporal memory** (`as_of`); **`COMPLETED != done`** (real Jules `verify`:
  state completed AND a branch on origin);
- **code-mode is the contract** (`search`/`get_schema`/`execute`) — exposed
  isomorphically over MCP and a **bash CLI** (Jules-dogfooded, PR #175);
- **code-mode tool-chaining**; **gates via `elicit`**;
- **schemas & templates** (typed/generative layer);
- a **strictly enforced ontology** (`ontology.py`: per-node required-field schemas
  + an enumerated edge set + closed enums; `record`/`link`/`update` reject drift);
- a **micro-step skill walker** (`skill.py`): one phase at a time (progressive
  disclosure) through a **hard gate**, recording each phase as provenance;
- **capabilities self-register by reflection** — the engine `discover()`s every
  `Capability` in `capabilities/` and auto-wires one MCP tool per verb from the
  verb signature (`inspect.signature`): adding a capability is adding a file;
- the **plugin-development capability** — a complete port of the superpowers
  skill-creation (`writing-skills`, Iron Law enforced by phase ordering) + plugin
  authoring (manifest · SKILL.md · command · marketplace entry · CSO linter);
- a **self-hosted install** — the engine authors and validates its own
  `.claude-plugin/plugin.json` + `help` macroskill (mapping macroskills → verbs);
- an **extensible, capability-owned ontology** — the core defines a base; each
  capability contributes its own node types / skills / template-schemas
  (`Capability.ontology`), merged strictly onto the core and enforced in Memory;
- the **`reflect` capability** — durable, scope-tagged cross-session memory
  (`note`/`recall`/`search` over `Reflection` nodes the capability owns).

The whole capability landscape of every installed plugin was surveyed, clustered,
and spec-paneled — see `CAPABILITY-CLUSTERS.md`. Verdict: the four concepts + the
engine absorb it all; the only net-new specs were **`delegate`** (agent fan-out +
quota + join) and **`reflect`** (durable cross-session memory) — `reflect` is now
built.

Next: build the `delegate` spec; grow the capability set by dropping files into
`capabilities/` (no wiring).
