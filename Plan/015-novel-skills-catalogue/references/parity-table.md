# Novel-Craft Parity Table (embedded brief)

> **Source**: research agent `a0c570a83e53508f8` ("Parity Table: bitwize-music → novel-writing MCP plugin roles"). This file embeds the **30-row music↔novel role mapping + 6 novel-specific additions + collapse/drop decisions + sources**. Cite this file from Spec 015's Approach and from every novel SKILL.md authored.

## Context (one paragraph)

Mapping each music-production role to its novel-writing counterpart, grounded in the standard four-stage editorial workflow (developmental → line → copy → proof) plus modern layered-revision practice. Researcher subroles carry over verbatim — they are domain-research utilities, not music-specific.

## Parity Table

| Music role | Novel counterpart | What it does for novels | Decision |
|---|---|---|---|
| `album-conceptualizer` | `novel-conceptualizer` | Premise, logline, theme, target reader, comp titles, series-arc hypothesis | Keep |
| `lyric-writer` | `prose-drafter` (a.k.a. `chapter-writer`) | Generates scene/chapter prose from outline + character/throughline brief | Keep |
| `lyric-reviewer` | `developmental-editor` (a.k.a. `prose-reviewer`) | Big-picture pass: structure, arc, pacing, character motivation, theme coherence (Stage 1 of 4-stage editorial workflow) | Keep |
| `lyric-refiner` | `line-editor` (a.k.a. `prose-refiner`) | Sentence-level pass: voice, rhythm, clarity, show-don't-tell, filter words (Stage 2) | Keep |
| `mix-engineer` | `revision-engineer` (a.k.a. `prose-revision-engineer`) | Layered revision passes (one lens at a time: dialogue, description, POV consistency) — Matt Bell / Susan Dennard "layered polish" model | Keep |
| — | `alpha-reader` / `beta-reader` / `critique-partner` | Pre-editorial human-feedback gates: alpha = early-draft sanity, critique-partner = peer-writer pass, beta = target-reader read | **Add** (no music analogue) |
| `mastering-engineer` | `copy-editor` | Grammar, punctuation, spelling, style-sheet adherence, internal consistency | Collapse (mastering family → 2 roles) |
| `mastering-engineer` (final polish) | `proofreader` | Final technical pass on typeset pages: typos, layout glitches, widow/orphan checks | Collapse with above |
| `master-with-reference` | — | Conform-to-reference-track has no clean novel analogue | **Drop** |
| `master-album` (whole-album mastering) | `manuscript-final-pass` | One sweep over entire manuscript for tonal consistency end-to-end | Collapse into copy/proof |
| `reset-mastering` | `revert-to-clean-draft` | Roll back edits, restart polish from a known-good draft | Keep (utility) |
| `polish-audio` / `polish-album` | `polish-pass` | Light cosmetic polish: word echoes, weak verbs, dialogue tag cleanup | Keep |
| `suno-engineer` | `prose-generation-prompt-engineer` | Crafts LLM prompts for scene drafting / expansion / style-transfer | Keep |
| `voice-checker` | `voice-consistency-checker` | Verifies narrator/POV voice stays consistent; flags drift between chapters | Keep |
| `pronunciation-specialist` | `narrator-voice-specialist` (a.k.a. `proper-noun-curator`) | Audiobook prep: phonetic guide for character names, made-up words, foreign terms; per-character voice direction notes | Keep |
| `plagiarism-checker` | `plagiarism-checker` | Cross-checks prose against corpora; flags accidental paraphrase | Keep verbatim |
| `explicit-checker` | `content-warning-checker` + `sensitivity-reader` | Flags explicit content for ratings AND flags stereotype/lived-experience issues — distinct crafts | **Split into 2** |
| `album-art-director` | `cover-art-director` | Cover concept, typography brief, series visual language | Keep |
| `promo-writer` | `blurb-writer` (a.k.a. `book-promo-writer`) | Back-cover copy, jacket flap, hook paragraph, log-line variants | Keep |
| `promo-director` | `marketing-copy-director` (a.k.a. `book-promo-director`) | Coordinates blurb, author bio, press kit, comp-title pitch | Keep |
| `sheet-music-publisher` | — | No analogue (sheet music is a music-only deliverable) | **Drop** |
| `release-director` | `publication-director` | Coordinates ISBN, metadata, distribution channels, launch timing; 9-domain QA gate | Keep |
| `validate-album` | `validate-manuscript` (a.k.a. `validate-work`) | Structural validation: chapter count, word count, front/back matter, file integrity | Keep |
| `album-coherence-check` | `manuscript-coherence-check` + `series-coherence-check` | (a) within-book continuity (timeline, names, world-rules) (b) across-series arc/canon | **Split into 2** |
| `pre-generation-check` | `pre-drafting-gate` (a.k.a. `pre-drafting-check`) | Before drafting a scene: storyform locked? throughline assigned? Q1–Q5 cleared? 6 BLOCKING gates | Keep |
| `album-dashboard` | `manuscript-dashboard` (a.k.a. `work-dashboard`) | Per-chapter status, word counts, beat-completion, revision-pass state | Keep |
| `document-hunter` | `document-hunter` | Finds source documents, archives, prior drafts | Keep verbatim |
| `verify-sources` | `verify-sources` | Confirms citations, historical claims, technical accuracy | Keep verbatim |
| `researchers-journalism` / `-primary-source` / `-historical` / `-biographical` / `-legal` / `-financial` / `-tech` / `-gov` / `-security` / `-verifier` (10 total) | same names | Domain research subroles — medium-agnostic | Keep verbatim (×10) |
| `album-ideas` / `genre-creator` | `novel-ideas` / `subgenre-creator` (a.k.a. `premise-ideas`) | Ideation backlog, genre-blend exploration | Keep |
| `import-track` / `import-audio` / `import-art` | `import-chapter` / `import-manuscript` / `import-cover` | Bring external files into project structure | Keep (rename) |
| `rename` / `next-step` / `resume` / `session-start` / `health-check` / `configure` / `tutorial` / `about` / `help` / `setup` | same names | Plugin lifecycle/admin — generic | Keep verbatim (lifecycle family) |

## Novel-specific additions (no music counterpart, 6 skills)

These map directly to Dramatica / NCP / Q1–Q5 work the music plugin doesn't need:

1. **`storyform-architect`** (a.k.a. **`work-architect`**) — locks Class/Type/Variation/Element selections per throughline (delegates to `dramatica-theory` + `dramatica-vocabulary`). Owns Storyform JSON. **Port verbatim from `agency/skills/novel-architect/`.**
2. **`dramatica-validator`** — runs the 75 Dynamic-Pair coherence checks, KTAD audit, Element-Quad integrity against the locked storyform. **Surfaces `novel_coherence_check` (Spec 013) as a skill.**
3. **`ncp-author`** — produces and validates `.ncp.json` artefacts against `ncp-schema.json v1.3.0`; owns enum-compliance and 10-stage authoring workflow. **Port verbatim from `agency/skills/ncp-author/`.**
4. **`scene-bridge-auditor`** — runs the Q1–Q5 Scene-Level-Bridge audit (Storyform → scene encoding) as a Phase-5/Phase-6 gate, per `novel-architect-scene`.
5. **`character-architect`** — applies TSDP/IFS, Big Five (OCEAN), Enneagram, Jung archetypes to NCP `players[]` slots (delegates Dramatica-vocab lookups). No music analogue because lyric "characters" are usually a single persona.
6. **`world-bible-architect`** — Phase-4 worldbuilding: domain mapping, canon bible; delegates deep research to `research-prompt-optimizer`. Music has no equivalent persistent world-state.

## Decisions (collapses + drops, one-line justifications)

- **Collapse: `mastering-engineer` + `mastering-engineer (final polish)` + `master-album` → `copy-editor` + `proofreader`.** Chicago Manual of Style names four editorial stages; the two terminal technical passes are pre-typeset (copy) and post-typeset (proof). A third "with-reference" mastering pass has no analogue.
- **Collapse: `polish-audio` + `polish-album` → single `polish-pass`.** Per-chapter vs whole-manuscript polish is a scope flag, not a separate role.
- **Drop: `master-with-reference`.** Conforming to a "reference mix" has no editorial analogue — novels aren't tonally matched to another novel as a deliverable.
- **Drop: `sheet-music-publisher`.** Pure music artefact; the closest novel equivalent (typesetting/interior design) lives under `publication-director`, not its own role.
- **Split: `album-coherence-check` → `manuscript-coherence-check` + `series-coherence-check`.** Series canon is a real long-horizon concern, distinct from within-manuscript consistency.
- **Split: `explicit-checker` → `content-warning-checker` + `sensitivity-reader`.** Content-warning/age-rating and authenticity reading are different crafts; sensitivity reads are now a standard editorial stage at major houses.
- **Add (no music source): `alpha-reader` / `critique-partner` / `beta-reader`.** Pre-editorial human-feedback gates have no music counterpart but are baseline novel practice.
- **Verbatim carry-over**: all `researchers-*`, `document-hunter`, `verify-sources`, `plagiarism-checker`. Domain research and integrity-checking are medium-agnostic.
- **Rename-only**: `lyric-*` → `prose-*` / editor variants, `album-*` → `manuscript-*` or `novel-*` or `work-*`, `suno-engineer` → `prose-generation-prompt-engineer`. Same role shape, different surface vocabulary.

## Skill total (used by Spec 015's Done When)

- **28 spirit-isomorphic skills** from the parity table (the editorial-stage and lifecycle column above).
- **4 ported storyform/theory skills** from `agency/`: `work-architect`, `dramatica-theory`, `dramatica-vocabulary`, `ncp-author`.
- **Grand total for Spec 015**: 28 + 4 = **32 novel SKILL.md files**.
- (The 10 prompt-builder skills are a separate family shipped by Spec 021.)

## Sources (12 citations)

- [Jane Friedman — Differences Between Line Editing, Copy Editing, and Proofreading](https://janefriedman.com/the-differences-between-line-editing-copy-editing-and-proofreading/) — four-stage editorial workflow grounding
- [MasterClass — What Is Line Editing? Line Editing vs. Copy Editing (2026)](https://www.masterclass.com/articles/what-is-line-editing) — current craft conventions, CMOS-aligned
- [Publish Her — Developmental / Line / Copy / Proofreading Explained](https://publishherpress.com/developmental-editing-line-editing-copy-editing-and-proofreading-explained/) — stage order and timing
- [Matt Bell — Refuse to Be Done](https://www.mattbell.com/refuse-to-be-done) — layered three-pass revision model (mix-engineer analogue)
- [Susan Dennard — A Guide to Revisions](https://stdennard.substack.com/p/a-guide-to-revisions) — macro→micro layered revision practice
- [Voices.com — Pronunciation Guides for Audiobook Narrators](https://www.voices.com/blog/pronunciation_guides/) — pronunciation-specialist analogue
- [CMOS Shop Talk — Preparing an Audiobook for a Narrator Who Isn't You](https://cmosshoptalk.com/2019/10/15/preparing-an-audiobook-for-a-narrator-who-isnt-you/) — per-character voice direction
- [Jericho Writers — Sensitivity Readers: Who They Are And What They Do](https://jerichowriters.com/sensitivity-readers/) — sensitivity-reader role definition
- [The Novelry — Do I Need a Sensitivity Reader? Authenticity Editing](https://www.thenovelry.com/blog/sensitivity-reader-authenticity-editing) — authenticity reading as editorial stage
- [School Library Journal — Sensitivity Readers Help Ensure Authentic Characters](https://www.slj.com/story/getting-it-right-sensitivity-readers-help-ensure-authentic-characters) — industry adoption at major houses
- [Reedsy — What is a Beta Reader?](https://reedsy.com/blog/beta-readers/) — alpha / beta / critique-partner ordering
- [Between the Lines Editorial — Alpha Readers, Beta Readers, and Critique Partners](https://btleditorial.com/2021/08/12/feedback-partners-writers/) — phase distinctions
