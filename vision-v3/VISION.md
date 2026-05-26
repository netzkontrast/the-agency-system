# agency — Vision (v3 draft, for adversarial review)

> Status: DRAFT under a ≥0.95 confidence gate. Not canon until certified.

## Purpose

`agency` is one Claude Code plugin: a single engine that lets an agent, for any
unit of work, answer the **six questions** that fully describe it — and execute
the **four** a machine can own.

## The founding idea — 5W1H

Any unit of work is fully described by six interrogatives. Two are human-owned
(**intent**); four are machine-executable:

| | Question | Owner | Is |
|---|---|---|---|
| **why** | why / to what end? | human | purpose + success criteria |
| **what** | what object? | human | the deliverable / subject |
| **who** | who acts? | engine | the agent / role |
| **how** | how is it done? | engine | the craft — skills, tools, actions |
| **when** | when / in what order? | engine | process: order, gates, lifecycle |
| **where** | where does it live? | engine | memory: the bi-temporal graph |

The human owns intent (why + what); the engine serves it through who/how/when/
where. Every action traces back, by edge, to the intent it serves.

## Principles (the north star)

1. **Self-explaining** — names carry their own meaning; the domains *are* the
   questions, so the system documents itself with zero glossary.
2. **Isomorphic** — one learnable shape repeats (the verb frame); learn one
   domain and you can predict the others.
3. **Token-efficient / context-engineering SOTA** — progressive disclosure,
   code-mode deltas, bi-temporal graph + ranked projection, compaction,
   ephemeral-subagent isolation.
4. **Harness-in-harness** — any agent (jules, codex, local subagents) is a
   first-class actor via the four-verb contract + an A2A boundary.
5. **Dogfoodable** — agency builds agency: the development loop is itself an
   agency workflow (intent → who/how/when/where).
6. **Protocol-compatible** — a first-class citizen of MCP, the Agent Skills
   spec, and A2A.
7. **Expressive enough** — can represent every skill, agent, and MCP tool in
   this repo *and beyond*.

## The goal

A clean, isomorphic concept; an initial commit of the Vision, the core ideas,
and initial specs of each system part + how they interact; demonstrated by one
**simple but complete** example.

## Governing principle

The Vision is authoritative. Prototype code is inspiration. Where they diverge,
the Vision wins.

## Process law

No checkpoint is "done" until **confidence ≥ 0.95**. Add a research step
whenever external input is needed. Every iteration: capture intent → research →
brainstorm → design → adversarial spec panel → review+gate → checkpoint.
