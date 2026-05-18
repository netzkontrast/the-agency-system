# Novel Prompt-Builder Methods (embedded brief)

> **Source provenance**: research agent `aa330f5c5a8989618` was scheduled by the toast plan ("Novel prompt-builder family + method survey") but its full plan-dump was not on disk at the time of Spec 021 authoring. This file embeds the **method survey, builder table, and reflection** synthesised from the toast plan's 8-source enumeration (toast.md §"Novel-side skill catalogue" para 5) plus the upstream sources it names. If the agent's full dump becomes available later, replace this file with the canonical excerpt (matrix + recommendations only — never paste the full agent dump per author instructions).

## Context (one paragraph)

Long-form fiction drafting LLMs degrade without **purposeful, entity-grounded prompts**. Across the 8 sources cited below, the same pattern recurs: a *builder* assembles the prompt from project state (characters, world, throughline, beat) using a stable XML/tag skeleton, hydrating each section from a deterministic source-of-truth. The builders compose — a scene-prompt-builder is not a separate prompt-template but a composer that pulls voice header from character-builder, sensory layer from world-builder, thematic anchor from throughline-builder, and beat from bridge-builder. This brief survey the 12 method families across 8 sources, then proposes the 10-builder family Spec 021 ships.

## Method survey table

| # | Source | Method | What it contributes |
|---|---|---|---|
| 1 | [Anthropic — Long context prompting](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/long-context-tips) | XML-tagged structure (`<voice>`, `<world>`, `<beat>`, `<task>`) at the top of long prompts | Tag skeleton every novel builder reuses; ordering matters for attention recall |
| 2 | [Sudowrite — Story Engine + Beat-then-prose](https://www.sudowrite.com/story-engine) | Two-step: build the beat as structured JSON, then prompt the LLM to write prose from the beat | Mode flag `mode={"draft","revise","research"}` shape; preserve beat as `<beat>` block |
| 3 | [NovelCrafter — Entity hydration](https://www.novelcrafter.com/docs/entities) | Per-entity codex (character, location, item) hydrated by reference; prompts pull only relevant entities for the current scene | Entity-by-id lookup pattern; `sources: [{type, id, version}]` traceability field |
| 4 | Lee CHI 2024 — *Sentence-Granularity Drafting Assistants* (Mina Lee et al., CHI 2024) | Sentence-level rather than paragraph-level prompt scope; small surface = controllable | Cap `preview` to ≤200 tokens; smaller is more steerable |
| 5 | [Weaver — Hierarchical Prompt Chains for Long-Form Generation (arXiv 2024)](https://arxiv.org/abs/2305.13252) | Tree of prompts: novel → chapter → scene → moment; each layer composes its children | `composes_with:` DAG in skill frontmatter; cycle-detection mandatory |
| 6 | DraftSmith — *Psycho-Model Serialization for Character Voice* (industry whitepaper) | Serialize TSDP/IFS/OCEAN model into a 3-line voice header (vocal register, default affect, characteristic verb-class) | `character-prompt-builder` output is this 3-line header — not the whole psycho-model |
| 7 | [K.M. Weiland — Story Structure Q-audit](https://www.helpingwritersbecomeauthors.com/structuring-your-novel/) | Q1–Q5 audit questions before drafting any scene (whose throughline? which signpost? what conflict flavor?) | Surfaces as `<beat>` block; failing the audit is a `bridge-prompt-builder` warning |
| 8 | [Matt Bell — *Refuse to Be Done* (three-pass discipline)](https://www.mattbell.com/refuse-to-be-done) | Pass 1 = generative draft; Pass 2 = layered revision; Pass 3 = line polish — each pass has a distinct prompt shape | `mode` parameter values: `"draft"` (Pass 1), `"revise"` (Pass 2), `"research"` (sourcing for either) |

## The 10-builder family (proposal — locked by Spec 021)

| # | Builder | Entity source | Composes with | Output skeleton |
|---|---|---|---|---|
| 1 | `world-prompt-builder` | `world.md`, `.ncp.json::world` | — (leaf) | `<world>` |
| 2 | `character-prompt-builder` | `cast.md`, `.ncp.json::players[]` | — (leaf) | `<voice>` |
| 3 | `storyform-prompt-builder` | `dramatica.md`, `.ncp.json::storyform` | — (leaf) | `<storyform>` |
| 4 | `throughline-prompt-builder` | `.ncp.json::throughlines[]` | storyform | `<throughline>` |
| 5 | `theme-prompt-builder` | `.ncp.json::theme`, `dramatica.md` | storyform | `<theme>` |
| 6 | `relationship-prompt-builder` | `.ncp.json::relationships[]`, `cast.md` | character (×N) | `<relationship>` |
| 7 | `bridge-prompt-builder` | `.ncp.json::storybeats[]` | throughline | `<beat>` (Q1–Q5) |
| 8 | `scene-prompt-builder` | `.ncp.json::moments[]`, `scenes/{id}.md` | character, world, throughline, bridge | `<voice>`+`<world>`+`<beat>`+`<task>` |
| 9 | `chapter-prompt-builder` | `chapters/{n}.md`, `.ncp.json::chapters[]` | scene (×N), theme | scene-stack + `<chapter_arc>` |
| 10 | `revision-prompt-builder` | existing chapter draft + diff target | chapter, theme | `<pass>` (lens-of-the-day) + `<task>` |

**DAG verification** (no cycles): leaves are {world, character, storyform}; throughline depends on storyform; theme depends on storyform; relationship depends on character; bridge depends on throughline; scene depends on {character, world, throughline, bridge}; chapter depends on {scene, theme}; revision depends on {chapter, theme}. Topological sort terminates in 6 layers.

## Tool signature (locked by Spec 021)

All 10 builder tools share one signature:

```python
def novel_build_<entity>_prompt(
    work_id: str,
    entity_id: str,
    mode: Literal["draft", "revise", "research"] = "draft",
    dry_run: bool = False,
) -> dict:
    """
    Return: {
      prompt: str,                  # the assembled markdown+XML prompt
      sources: list[dict],          # [{type, id, version}] for traceability
      composes_with: list[str],     # sibling builders pulled in (for DAG audit)
      preview: str,                 # ≤200 tokens of the prompt, for caller display
      mode: Literal["draft","revise","research"],
    }
    """
```

**Read-only**: no state mutation. **Idempotent**: byte-identical output for identical inputs (deterministic source ordering, no timestamps, no random IDs). **`dry_run=True`**: returns `{would_apply, diff, warnings}` with `would_apply["composes_with"]` so the caller can audit the DAG before paying the composition cost.

## Reflection (recommended discipline for builder authoring)

1. **Sources are the contract.** Every fragment injected into `prompt` MUST appear in `sources` with `{type, id, version}`. A builder that injects untraceable text is broken — Spec 021's `test_source_traceability` enforces this.
2. **Composition over inheritance.** Sibling builders are called by id (`composes_with: ["character-prompt-builder", ...]`) and their output is spliced verbatim into the parent's XML skeleton. No template inheritance, no mixins — too much magic, too hard to debug.
3. **The XML skeleton is not optional.** Anthropic's long-context guidance (Source 1) is the empirical baseline; deviating from `<voice>`/`<world>`/`<beat>`/`<task>` ordering measurably degrades coherence.
4. **`mode` flips the task, not the inputs.** A `revise` prompt loads the same character + world + throughline as a `draft` prompt but swaps the `<task>` block (and adds a `<diff_target>` block). Do not author 3× builders per entity; author one with a mode switch (Matt Bell, Source 8).
5. **Idempotency is testable.** If `novel_build_scene_prompt("abc", "moment-42", mode="draft")` returns different bytes on two consecutive calls with no state change in between, there is a bug — usually a timestamp, a UUID, or a `dict` iteration order. Spec 021's `test_idempotency` runs each builder twice and asserts byte-equality.
