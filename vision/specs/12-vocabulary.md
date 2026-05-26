---
slug: vision-vocabulary
type: spec
status: ready
owner: claude
created: 2026-05-20
updated: 2026-05-20
summary: Single lexicon for the agency-system. Defines the three-layer harness ladder (L1/L2/L3), the four-verb contract surface, the five handler-bearing domains plus agentic, the Path A vs Path B disambiguation, frontmatter conventions, repair-authority tiers, and content tiers. Other vision/ specs cite this file for canonical terminology.
depends_on:
  - vision/specs/02-tool-result-envelope.md
  - vision/specs/06-agentic-base.md
  - vision/specs/09-crossover-matrix.md
referenced_by:
  - vision/specs/10-harness-ladder.md
  - vision/specs/11-four-verb-canon.md
  - vision/specs/13-domain-isomorphism.md
  - vision/specs/14-progressive-disclosure-roadmap.md
supersedes:
  - Plan/harness/VOCABULARY.md
---

# Harness Vocabulary — Canonical naming & cross-reference index

This is the single-source-of-truth lexicon for the unified `agency-system` plugin. It extracts terminology introduced in the architecture pillars so every downstream document can reference it without re-deriving the canon.

## §1 Token-budget invariants

The unified plugin has **one** unified token budget. Every phase aligns against these strict constraints:

| Invariant | Value | Source |
|---|---|---|
| Boot context budget (cold) | < 500 tokens | `vision/specs/09-crossover-matrix.md` §3 bullet 3 lines 132-138 |
| `tools/list` cold payload | < 4 KB | `vision/specs/09-crossover-matrix.md` §3 bullet 3 lines 132-138 |
| Per-tool result max in context | ≤ 4 KB → archived via `data.artefact_ref` | `vision/specs/02-tool-result-envelope.md` line 65; `vision/specs/09-crossover-matrix.md` §3 lines 132-138 |

## §2 Three-layer harness ladder (L1/L2/L3)

The harness is a **three-layer ladder** that exposes the same four-verb contract via three transports at three fidelity tiers. Cross-reference `vision/specs/10-harness-ladder.md` for the full ladder spec.

| Layer | Audience | Transport | Boot cost | Status |
|---|---|---|---|---|
| **L1 In-process harness** | pytest, Phase 1+ smoke tests, dev iteration | FastMCP in-memory (`tests/_harness/`) | ms | **Shipped** |
| **L2 Subprocess probe** | CI boot-fidelity backstop | `claude --bare --plugin-dir <repo> --debug plugins -p exit` | ~seconds + small API cost | **Shipped** |
| **L3 Sidecar daemon + CLI** | external agents, bash-only LLMs | FastMCP Streamable HTTP on `127.0.0.1:7777` | ~3-5s cold boot | **Planned** |

**Cross-layer isomorphism invariant:** at every layer L, a call to verb V with envelope E produces tool_result T(V, E) independent of L.

## §3 Four-verb contract

The canonical four verbs define the exact interface available across all layers and inter-column boundaries. These use standard MCP tool naming prefixes. Cross-reference `vision/specs/11-four-verb-canon.md` for details.

1. `mcp__list_tools`
2. `mcp__call_tool`
3. `mcp__list_skills`
4. `mcp__dispatch_skill`

## §4 Five handler-bearing domains plus agentic

Each domain has handlers under `<domain>/<row>/handlers/`.

| Domain | Role | Note |
|---|---|---|
| `music` | music projects | flagship domain |
| `novel` | novel projects | |
| `jules` | Jules async-coding orchestration | low skill surface by design |
| `context` | Context Mode Path B manifest & anchor triad | tool-only domain |
| `shared` | cross-domain primitives | tool-only domain |
| `agentic` | meta-domain | **skill-only domain** |

## §5 Naming canon

Canonical naming schemes apply universally across the codebase; spec 09 §3.1 and §3.5 cite this:

| Pattern | Examples | Reference |
|---|---|---|
| Tool names (export) | `mcp__<row>_<export>` | `mcp__music_analysis` |
| Skill slugs | `<row>:<skill>` | `agentic:spec-writer` |
| Phase node IDs | `phase:<row>/<phase_id>` | `phase:music/mastering` |

## §6 Frontmatter conventions

Every canonical artefact MUST carry a frontmatter block with basic required keys: `slug`, `type`, `status`, `owner`, `created`, `updated`, and `summary`.
Additionally, **Reciprocity-as-invariant rules** dictate:
- `depends_on:` requires no backward link.
- `referenced_by:` reciprocity must be manually maintained on both ends.
- `supersedes:` + `superseded_by:` strictly require reciprocal pointers on both the predecessor and successor.

## §7 Repair-authority tiers

Changes follow strict tiers to clarify responsibility and impact:

| Tier | Scope | Allowed Actions |
|---|---|---|
| **T1 Mechanical** | typos, links, formatting | in-place fix |
| **T2 Additive** | isolated new info | in-place fix |
| **T3 Structural** | reordering, claim change | Must open a Task/spec |
| **T4 Immutable** | accepted ADRs, historical | MUST NOT mutate |

## §8 Content tiers

Every artefact has three content tiers loaded progressively. Distinct from Plan/ records:
- **T1 Trigger**: ≤ 200 chars abstract.
- **T2 Body**: ≤ 5 KB full document.
- **T3 References**: unlimited sub-directory.
Note: **vision/** artefacts represent canon whereas **Plan/** artefacts represent draft/history.

## §9 Path A vs Path B disambiguation

There are two separate concepts referred to as Path A / Path B. Here we disambiguate the Domain restructure:

- **Harness Path A** (active lever): incremental levers in current state.
- **Harness Path B** (vision-only): full domain isomorphism restructure. Cross-reference `vision/specs/13-domain-isomorphism.md` for Path B.

## §10 Cited-by table

Other `vision/` files expected to cite this vocabulary document:

| Expected Citing Document |
|---|
| `vision/specs/10-harness-ladder.md` |
| `vision/specs/11-four-verb-canon.md` |
| `vision/specs/13-domain-isomorphism.md` |
| `vision/specs/14-progressive-disclosure-roadmap.md` |
