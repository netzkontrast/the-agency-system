# agency-seed

A **running** proof of the v4 core (see `../vision-v3/CORE.md`) on the **real
substrate** — `graphqlite` (SQLite + Cypher) + `fastmcp` (incl. the experimental
code-mode transform). Built after the adversarial spec panel's unanimous verdict:
*stop spec'ing, build the smallest thing that proves the moat and falsifies the
risks.*

## What it proves (`tests/test_seed.py`, 7/7 green)

1. **The moat — cross-concern provenance is one graph traversal.**
   `Memory.provenance(intent)` returns, in one Cypher walk, every action that
   `SERVES` the intent, the agent that `PERFORMED_BY` it, the artefact it
   `PRODUCES`d, and the gate it `PASSED`. A flat SDK+memory-tool stack needs a
   join across four systems for this.
2. **One graph + the verb frame carry two genuinely different capabilities** — a
   stateless `transform` (`count_syllables`) and an `agent` (`jules`). This is
   the panel's falsifier; it holds.
3. **Bi-temporal memory** — the *what* changes while the *why* holds; the prior
   version is reconstructable `as_of` an earlier tick (append-only `supersede`).
4. **`COMPLETED != done`** — the jules silent-fail lesson as a first-class
   `verify` step.
5. **Code-mode IS the contract** — the engine surface is exactly
   `search` / `get_schema` / `execute` (no four-verb list); tools are discovered
   via `search` and called from inside `execute`. MCP-conformant names.
6. **Code-mode tool-chaining = an executable graph.** An `execute` block chains
   `transform → agent` in plain Python; 4 tool calls run in-sandbox and only a
   single small delta crosses into context (**token efficiency** — the −98%
   pattern), while every call records an Invocation, so the executable dataflow
   graph is **mirrored into the durable provenance graph**.
7. **Gates / human-in-the-loop via `elicit`** — a gate step asks the human/agent
   a one-line question mid-flow (askuser-in-the-flow) and records the outcome as
   a `Gate`.
8. **Bash ≡ MCP isomorphism** — the same code-mode contract driven via MCP *and*
   via a bash-only subprocess, over the same graph, yields identical results.
   This is what lets Jules run the engine with no MCP/Skill integration — see
   `AGENTS.md`.

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## Layout

| File | Concept |
|---|---|
| `agency_seed/memory.py` | **Memory** — bi-temporal graph on GraphQLite; `record·link·supersede` / `recall·find·validate`; `project` (budgeted); `provenance` (the moat) |
| `agency_seed/intent.py` | **Intent** — `capture·confirm·amend` (why/what merged) |
| `agency_seed/lifecycle.py` | **Lifecycle** — `open·move·complete·status`; A2A-aligned states; agent parameterization; gates |
| `agency_seed/capability.py` + `capabilities/` | **Capability** — open verbs, role-tagged `act·transform·effect`; `syllables` (transform), `jules` (agent) |
| `agency_seed/engine.py` | **Engine** — FastMCP; **code-mode** (`search`/`get_schema`/`execute`) is the contract |
| `agency_seed/cli.py` + `AGENTS.md` | **Bash layer** — the same code-mode contract over a CLI, for bash-only agents (Jules) |

> Status: a proof-of-concept seed, not the shipped engine. It exists to make the
> v4 claims *runnable and falsifiable* rather than spec-only.
