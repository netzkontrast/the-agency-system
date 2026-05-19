---
slug: vision-readme
type: vision-charter
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: Three independent Jules agents — one per column of the 3×N matrix — collaboratively produce the system's core specification.
---

# `/vision` — three column-owning Jules agents

The agency-system base is a **3-column × N-row matrix** of cells. The
columns are fixed: `agentic`, `workflow`, `context`. The rows are
domains (music, novel, jules, podcast, …). Every cell has one canonical
shape; every row has three cells.

This folder holds the briefs for three independent Jules agents, each
of which **owns one column** of the matrix. The merge product of the
three agents' outputs is the system spec.

## Files

- [`00-charter.md`](00-charter.md) — the shared inheritance every agent
  must read first: matrix law, three rules, meta-row, 18 Gherkin
  scenarios, source repos, discipline. Agent-agnostic.
- [`agentic/BRIEF.md`](agentic/BRIEF.md) — instructions for the agent
  owning the **agentic** column (skills + MCP + harness-in-harness).
- [`workflow/BRIEF.md`](workflow/BRIEF.md) — instructions for the agent
  owning the **workflow** column (pipelines + handoffs + gates +
  meta-row).
- [`context/BRIEF.md`](context/BRIEF.md) — instructions for the agent
  owning the **context** column (graph + frontmatter + search + pandoc
  + templates + schemas).

## Why columns, not stances

Earlier Jules sessions split by stance (critical / improvements /
from-scratch). The stance split produced three valuable but partly
overlapping artefacts. This column split produces three **strictly
non-overlapping** artefacts whose union IS the spec. The trade-off is
explicit: less critical pressure, more constructive coverage.

## Merge guarantee

Each agent writes its outputs only under `vision/<their-column>/`.
The three folders are merge-orthogonal. The three `INTERFACES.md`
files form a triangle of contracts — the merge check is that contracts
declared by column X for column Y match contracts declared by Y for X.
